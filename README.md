# todolist-repo

# DevOps To-Do List App

A simple full-stack To-Do List application built with Flask and vanilla JavaScript. This project was created as a hands-on learning exercise to cover all layers of a modern web application, from the front-end to the back-end database.

## Features

* View all to-do items.
* Add a new to-do item.
* Delete an existing to-do item.

## Tech Stack

* **Backend:** Python, Flask, Flask-SQLAlchemy
* **Database:** SQLite
* **Frontend:** HTML, CSS, vanilla JavaScript

## Setup and Installation

To run this project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/grimm00/todolist-repo.git](https://github.com/grimm00/todolist-repo.git)
    cd todolist-repo
    ```

2.  **Create and activate a Python virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies from `requirements.txt`:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the database:**
    ```bash
    flask shell
    >>> from app import db
    >>> db.create_all()
    >>> exit()
    ```

5.  **Run the application:**
    ```bash
    flask --app app --debug run
    ```
    The application will be running at `http://127.0.0.1:5000`.