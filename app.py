from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from google.cloud.sql.connector import Connector
import sqlalchemy
import os

# --- Find the absolute path of the project directory ---
basedir = os.path.abspath(os.path.dirname(__file__))

# Create a Flask application instance
app = Flask(__name__)
# Add a secret key for session management
app.config['SECRET_KEY'] = os.urandom(24) 

# --- DATABASE CONFIGURATION ---
# Function to initialize a connection pool to the Cloud SQL database
def init_connection_pool() -> sqlalchemy.engine.base.Engine:
    """Initializes a connection pool for a Cloud SQL instance."""
    # The Cloud SQL Python Connector is the recommended way to connect.
    connector = Connector()

    # Function to return database credentials and establish a connection
    def get_conn() -> sqlalchemy.engine.interfaces.DBAPIConnection:
        # The instance connection name is a required environment variable.
        INSTANCE_CONNECTION_NAME = os.environ["INSTANCE_CONNECTION_NAME"]
        # Database credentials are automatically injected by Cloud Run from Secret Manager.
        DB_USER = os.environ["DB_USER"]
        DB_PASS = os.environ["DB_PASS"]
        DB_NAME = os.environ["DB_NAME"]
        
        conn = connector.connect(
            INSTANCE_CONNECTION_NAME,
            "pg8000",
            user=DB_USER,
            password=DB_PASS,
            db=DB_NAME,
        )
        return conn

    # Create a SQLAlchemy engine with the connection function.
    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=get_conn,
    )
    return pool

# Check if running in Cloud Run, otherwise use the local instance folde
if os.environ.get("K_SERVICE"):
    # For Cloud Run, connect to the Cloud SQL production database.
    db_pool = init_connection_pool()
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+pg8000://"
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"creator": db_pool.connect}
else:
    # Create an absolute path for the local database
    instance_path = os.path.join(basedir, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    db_uri = f"sqlite:///{os.path.join(instance_path, 'database.db')}"
    
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Redirect to login page if user is not authenticated

# --- User Loader for Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- DATABASE MODEL DEFINITIONS ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(150), nullable=False)
    todos = db.relationship('Todo', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {'id': self.id, 'task': self.task, 'completed': self.completed}

# Create database tables
with app.app_context():
    db.create_all()

# --- WEB PAGE ROUTES ---
@app.route('/')
def index():
    # You will need to update index.html to handle user sessions
    return render_template('index.html')

# --- AUTHENTICATION ROUTES ---
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user:
        return jsonify({"error": "Username already exists"}), 409
    
    new_user = User(username=data['username'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    return jsonify({"success": "User registered and logged in", "user": {"id": new_user.id, "username": new_user.username}}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({"success": "Logged in", "user": {"id": user.id, "username": user.username}})
    
    return jsonify({"error": "Invalid username or password"}), 401

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"success": "Logged out"})

# --- API ENDPOINTS (NOW PROTECTED) ---
@app.route('/api/todos', methods=['GET'])
@login_required
# GET all to-do items
def get_todos():
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    return jsonify([todo.to_dict() for todo in todos])

# POST a new to-do item
@app.route('/api/todos', methods=['POST'])
@login_required
def create_todo():
    data = request.get_json()
    new_todo = Todo(task=data['task'], author=current_user)
    db.session.add(new_todo)
    db.session.commit()
    return jsonify(new_todo.to_dict()), 201

# DELETE a to-do item
@app.route('/api/todos/<int:id>', methods=['DELETE'])
@login_required
def delete_todo(id):
    todo = Todo.query.filter_by(id=id, user_id=current_user.id).first()
    if todo is None:
        return jsonify({"error": "Todo not found or not owned by user"}), 404
    
    db.session.delete(todo)
    db.session.commit()
    return jsonify({"success": "Todo deleted"})

# -----------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)