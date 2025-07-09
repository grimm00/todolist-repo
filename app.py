from flask import Flask, jsonify

# Create a Flask application instance
app = Flask(__name__)

# This is our temporary in-memory "database" for now
# We'll replace this with a real database later.
todos = [
    {"id": 1, "task": "Learn Docker", "completed": False},
    {"id": 2, "task": "Build a Flask API", "completed": True},
]

# Define a route to get all to-do items
@app.route('/api/todos', methods=['GET'])
def get_todos():
    return jsonify(todos)

# This makes the app runnable
if __name__ == '__main__':
    app.run(debug=True)