from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import os

# --- Find the absolute path of the project directory ---
basedir = os.path.abspath(os.path.dirname(__file__))

# Create a Flask application instance
app = Flask(__name__)

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

@app.route('/')
def index():
    return render_template('index.html')

# --- DATABASE MODEL DEFINITION ---
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'task': self.task,
            'completed': self.completed
        }
        
with app.app_context():
    db.create_all()

# --- API ENDPOINTS ---


# GET all to-do items
@app.route('/api/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    return jsonify([todo.to_dict() for todo in todos])

# POST a new to-do item
@app.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    new_todo = Todo(task=data['task'])
    db.session.add(new_todo)
    db.session.commit()
    return jsonify(new_todo.to_dict()), 201

# DELETE a to-do item
@app.route('/api/todos/<int:id>', methods=['DELETE'])
def delete_todo(id):
    todo = Todo.query.get(id)
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404
    
    db.session.delete(todo)
    db.session.commit()
    return jsonify({"success": "Todo deleted"})

# -----------------------

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Flask on port {port}, database at {db_uri}")
    app.run(host="0.0.0.0", port=port)


