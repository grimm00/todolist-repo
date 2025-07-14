from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import os

# --- Find the absolute path of the project directory ---
basedir = os.path.abspath(os.path.dirname(__file__))

# Create a Flask application instance
app = Flask(__name__)

# Add a secret key, which is required by Flask-Login to securely sign the session cookie.
app.config['SECRET_KEY'] = os.urandom(24)

# --- DATABASE CONFIGURATION ---

# Check if running in Cloud Run, otherwise use the local instance folder
if os.environ.get("K_SERVICE"):
    # For Cloud Run, use the temporary directory
    db_uri = "sqlite:////tmp/database.db"
else:
    # Create an absolute path for the local database
    instance_path = os.path.join(basedir, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    db_uri = f"sqlite:///{os.path.join(instance_path, 'database.db')}"
    
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app) # Initialize BCrypt
login_manager = LoginManager(app) # Initialize Flask-Login
# If a user tries to access a @login_required route without being logged in,
# Flask-Login will return a 401 Unauthorized error, which is perfect for an API.
login_manager.login_view = ''

# --- DATABASE MODEL DEFINITIONS ---

# The user_loader is a function that Flask-Login uses to reload a user object from the user ID stored in the session.
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# The User model inherits from UserMixin, which adds the required properties for Flask-Login to work.
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(150), nullable=False)
    todos = db.relationship('Todo', backref='author', lazy=True)  # This relationship links a User to all of their Todo items.

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # This foreign key column links each Todo to a User.

    def to_dict(self):
        return {
            'id': self.id,
            'task': self.task,
            'completed': self.completed
        }
             
with app.app_context():
    db.create_all()

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

# Route for registering a new user
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400

    # Check if user already exists
    user = User.query.filter_by(username=data['username']).first()
    if user:
        return jsonify({"error": "Username already exists"}), 409
    
    # Create new user and hash the password
    new_user = User(username=data['username'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"success": f"User '{new_user.username}' created."}), 201

# Route for logging a user in
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()

    # Check if the user exists and the password is correct
    if user and user.check_password(data.get('password', '')):
        # login_user is a special Flask-Login function that creates the session
        login_user(user)
        return jsonify({"success": "Logged in successfully."})
    
    return jsonify({"error": "Invalid username or password"}), 401 # 401 is the "Unauthorized" status code

# Route for logging a user out
@app.route('/logout', methods=['POST'])
def logout():
    # logout_user is a special Flask-Login function that clears the session
    logout_user()
    return jsonify({"success": "Logged out successfully."})
# --- API ENDPOINTS ---

# GET all to-do items for the logged-in user
@app.route('/api/todos', methods=['GET'])
@login_required # <-- This endpoint is now protected
def get_todos():
    todos = Todo.query.filter_by(author=current_user).all() # NEW: Filter todos to only get ones authored by the current_user
    return jsonify([todo.to_dict() for todo in todos])

# POST a new to-do item for the logged-in user
@app.route('/api/todos', methods=['POST'])
@login_required # <-- This endpoint is now protected
def create_todo():
    data = request.get_json()
    new_todo = Todo(task=data['task'], author=current_user) # NEW: Assign the current_user as the author of the new todo
    db.session.add(new_todo)
    db.session.commit()
    return jsonify(new_todo.to_dict()), 201

# DELETE a to-do item
@app.route('/api/todos/<int:id>', methods=['DELETE'])
@login_required # <-- This endpoint is now protected
def delete_todo(id):
    # NEW: Query for the todo, ensuring it belongs to the current_user
    todo = Todo.query.filter_by(id=id, user_id=current_user.id).first()
    if todo is None:
        return jsonify({"error": "Todo not found or you do not own this todo"}), 404
    
    db.session.delete(todo)
    db.session.commit()
    return jsonify({"success": "Todo deleted"})

# -----------------------

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting Flask on port {port}, database at {db_uri}")
    app.run(host="0.0.0.0", port=port)


