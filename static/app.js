// --- DOM Element References ---
// Get references to the HTML elements we'll be interacting with.

// Auth elements
// References for Authentication and UI containers ---
const authContainer = document.getElementById('auth-container');
const todoContainer = document.getElementById('todo-container');
const userStatusContainer = document.getElementById('user-status');
const registerForm = document.getElementById('register-form');
const loginForm = document.getElementById('login-form');
const logoutButton = document.getElementById('logout-button');
const usernameDisplay = document.getElementById('username-display');
const registerUsernameInput = document.getElementById('register-username');
const registerPasswordInput = document.getElementById('register-password');
const loginUsernameInput = document.getElementById('login-username');
const loginPasswordInput = document.getElementById('login-password');

// To-Do elements
const todoForm = document.getElementById('todo-form');
const todoInput = document.getElementById('todo-input');
const todoList = document.getElementById('todo-list');

// Status and Error elements
const statusText = document.getElementById('status-text');
const errorMessage = document.getElementById('error-message');

console.log("app.js loaded successfully. All elements referenced.");

// --- NEW: UI Management ---

/**
 * Updates the UI based on the user's login state.
 * @param {boolean} isLoggedIn - Whether the user is currently logged in.
 * @param {string} [username] - The username to display if logged in.
 */
const updateUI = (isLoggedIn, username) => {
    if (isLoggedIn) {
        // If logged in:
        // Hide the authentication forms.
        authContainer.classList.add('hidden');
        // Show the to-do list container and the user status area.
        todoContainer.classList.remove('hidden');
        userStatusContainer.classList.remove('hidden');
        // Display the user's name.
        usernameDisplay.textContent = username;
        // Fetch and display the user's to-do items.
        fetchTodos();
    } else {
        // If not logged in:
        // Show the authentication forms.
        authContainer.classList.remove('hidden');
        // Hide the to-do list and user status area.
        todoContainer.classList.add('hidden');
        userStatusContainer.classList.add('hidden');
        // Clear the to-do list to ensure no old data is shown.
        todoList.innerHTML = '';
    }
};

// --- FUTURE: API Helper Function ---
/**
 * A helper function to handle fetch requests and basic error handling.
 * @param {string} url - The URL to fetch.
 * @param {object} [options={}] - The options for the fetch request.
 * @returns {Promise<object|null>} - The JSON response from the API or null on error.
 
const apiRequest = async (url, options = {}) => {
    // This option is crucial for sending the session cookie in later steps.
    options.credentials = 'include'; 

    try {
        const response = await fetch(url, options);
        const data = await response.json(); // Always try to parse JSON
        if (!response.ok) {
            // If the server returns an error (e.g., status 400, 409), display it.
            errorMessage.textContent = data.error || 'An unknown error occurred.';
            console.error('API Error:', data);
            return null;
        }
        errorMessage.textContent = ''; // Clear errors on success
        return data;
    } catch (error) {
        errorMessage.textContent = 'Network error. Is the server running?';
        console.error('Request Failed:', error);
        return null;
    }
};
 */


// --- NEW: Event Handlers ---

/**
 * Handles user registration by sending a request to the /register endpoint.
 */
const handleRegister = async (event) => {
    event.preventDefault(); // Prevent the form from reloading the page
    const username = registerUsernameInput.value;
    const password = registerPasswordInput.value;

    const response = await fetch('/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
    });

    const data = await response.json();

    if (response.ok) {
        alert('Registration successful! Please log in.');
        registerForm.reset(); // Clear the registration form fields
    } else {
        alert(`Registration failed: ${data.error}`); // Show the error from the server
    }
};

/**
 * Handles user login by sending a request to the /login endpoint.
 */
const handleLogin = async (event) => {
    event.preventDefault();
    const username = loginUsernameInput.value;
    const password = loginPasswordInput.value;

    const response = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
    });

    if (response.ok) {
        // --- THIS IS A KEY STEP ---
        // On successful login, call updateUI to change the view.
        sessionStorage.setItem('username', username); // Temporarily store username for display
        updateUI(true, username);
        loginForm.reset();
    } else {
        alert('Login failed. Check your username and password.');
    }
};

/**
 * Handles user logout by sending a request to the /logout endpoint.
 */
const handleLogout = async () => {
    await fetch('/logout', { method: 'POST' });
    sessionStorage.removeItem('username'); // Clear stored username
    // Call updateUI to return to the logged-out view.
    updateUI(false);
};

/**
 * Checks if the user is already logged in by calling the /api/me endpoint.
 */
const checkLoginStatus = async () => {
    const response = await fetch('/api/me'); // Call the new endpoint

    if (response.ok) {
        // If the request is successful, the user is logged in.
        const user = await response.json(); // Get the user data { "username": "..." }
        updateUI(true, user.username); // Update the UI with the username from the server
    } else {
        // If the request fails (e.g., 401 Unauthorized), the user is not logged in.
        updateUI(false);
    }
};


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

// --- Event Listeners & Initial Page Load ---
// This section 'wires up' all user interactions and starts the app

// Use the 'submit' event for forms to capture when the user presses Enter or clicks the submit button.
registerForm.addEventListener('submit', handleRegister);
loginForm.addEventListener('submit', handleLogin);

// Use the 'click' event for the logout button.
logoutButton.addEventListener('click', handleLogout);

// Add an event listener to the form to call addTodo when it's submitted.
todoForm.addEventListener('submit', addTodo);

// Finally, check the user's login status when the page is fully loaded.
document.addEventListener('DOMContentLoaded', checkLoginStatus);