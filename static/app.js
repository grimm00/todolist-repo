// Get references to the HTML elements we'll be interacting with.
const todoForm = document.getElementById('todo-form');
const todoInput = document.getElementById('todo-input');
const todoList = document.getElementById('todo-list');

// This function fetches all todos from the API and displays them.
const fetchTodos = async () => {
    // Make a GET request to our API.
    const response = await fetch('/api/todos');
    const todos = await response.json();

    // Clear the current list before displaying the new ones.
    todoList.innerHTML = '';

    // Loop through each todo item and create an HTML list item for it.
    todos.forEach(todo => {
        const li = document.createElement('li');
        li.textContent = todo.task;

        const deleteButton = document.createElement('button');
        deleteButton.textContent = 'Delete';
        // Add an event listener to handle deleting this specific todo.
        deleteButton.onclick = () => deleteTodo(todo.id);

        li.appendChild(deleteButton);
        todoList.appendChild(li);
    });
};

// This function handles creating a new todo.
const addTodo = async (event) => {
    // Prevent the default form submission which reloads the page.
    event.preventDefault();

    const task = todoInput.value;

    // Make a POST request to our API with the new task.
    await fetch('/api/todos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ task: task }),
    });

    // Clear the input field and refresh the list.
    todoInput.value = '';
    fetchTodos();
};

// This function handles deleting a todo.
const deleteTodo = async (id) => {
    // Make a DELETE request to our API for the specific id.
    await fetch(`/api/todos/${id}`, {
        method: 'DELETE',
    });

    // Refresh the list to show the item has been removed.
    fetchTodos();
};

// Add an event listener to the form to call addTodo when it's submitted.
todoForm.addEventListener('submit', addTodo);

// Fetch and display all todos when the page first loads.
fetchTodos();