# --- Stage 1: The "builder" stage ---
# We use the full python image here because it has the necessary build tools.
# We give this stage a name, "builder", so we can refer to it later.
FROM python:3.11 as builder

# Set the working directory
WORKDIR /app

# Install all Python dependencies. These will be copied to the next stage.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- This is the key part for your local debugging ---
# Install the sqlite3 command-line tool ONLY in this builder stage.
RUN apt-get update && apt-get install -y sqlite3

# Copy the rest of the application code
COPY . .

# This tells the development container what command to run.
# It will be overridden by the final CMD in the production stage.
EXPOSE 5000
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
CMD ["python", "app.py"]


# --- Stage 2: The final "production" stage ---
# We start fresh with the lightweight "slim" image for our final container.
FROM python:3.11-slim

WORKDIR /app

# Copy the installed Python packages from the "builder" stage.
# This is much faster than running "pip install" again.
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy the application code from the "builder" stage.
COPY --from=builder /app .

# Expose the port and set the final command, just like before.
EXPOSE 8080
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
# CMD ["python", "app.py"] - Old Production
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
