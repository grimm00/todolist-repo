# DevOps To-Do List App

[![Version](https://img.shields.io/badge/version-v0.2.1-blue)](https://github.com/grimm00/todolist-repo/releases)

A full-stack To-Do List application built with Flask and vanilla JavaScript, containerized with Docker, and deployed via an automated CI/CD pipeline to Google Cloud Run. This project was created as a hands-on learning exercise to cover all layers of a modern web application and its deployment workflow.

## Table of Contents

1.  [Features](#features)
2.  [Tech Stack](#tech-stack)
3.  [Running the Application](#running-the-application)
4.  [CI/CD Pipeline](#cicd-pipeline)
5.  [Future Improvements](#future-improvements)

---

## Features

* **User Authentication:**
    * Register for a new account.
    * Log in and log out securely.
* **To-Do Management:**
    * Create and delete personal to-do items that are tied to your user account.

---

## Tech Stack

* **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login
* **Frontend:** HTML, CSS, Vanilla JavaScript
* **Database:** SQLite
* **Containerization:** Docker
* **Production Server:** Gunicorn
* **CI/CD:** GitHub Actions
* **Deployment:** Google Cloud Run

---

## Running the Application

This project is fully containerized, so the only prerequisite is **Docker**. You do not need to install Python or any dependencies on your local machine.

### 1. Local Development Environment

This mode uses the Flask development server and is ideal for making and testing changes.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/grimm00/todolist-repo.git](https://github.com/grimm00/todolist-repo.git)
    cd todolist-repo
    ```

2.  **Make the helper script executable:**
    ```bash
    chmod +x run_local.sh
    ```

3.  **Run the script:**
    ```bash
    ./run_local.sh
    ```
    The application will be running at `http://localhost:5000`.

### 2. Local Production Environment

This mode simulates the final production environment, using the lightweight Docker image and the Gunicorn server. It's perfect for a final check before deployment.

1.  **Make the helper script executable:**
    ```bash
    chmod +x run_prod.sh
    ```
2.  **Run the script:**
    ```bash
    ./run_prod.sh
    ```
    The application will be running at `http://localhost:8080`.

---

## CI/CD Pipeline

This project uses a GitHub Actions workflow (`.github/workflows/main.yml`) for continuous integration and deployment. The pipeline is triggered on every `push` to the `main` branch.

The key steps in the pipeline are:
1.  **Checkout Code:** The workflow checks out the repository's code.
2.  **Authenticate to Google Cloud:** It securely authenticates with Google Cloud using Workload Identity Federation.
3.  **Build & Test Docker Image:** It builds the production Docker image and runs it inside the GitHub Actions runner, sending a test request to ensure it's working correctly.
4.  **Push Docker Image:** If the test passes, it pushes the image to the Google Artifact Registry.
5.  **Deploy to Cloud Run:** It deploys the new image to Google Cloud Run, making the update live.

---

## Future Improvements

- **Persistent Database:** The current deployment uses a temporary database that is wiped on new deployments. The next major step is to integrate a managed, persistent database like **Google Cloud SQL** or **Firestore**.
- **Enhanced Frontend:** Improve the user experience by replacing `alert()` messages with modern UI notifications and adding more features like editing tasks or marking them as complete.
