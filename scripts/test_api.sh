#!/bin/bash

# This script automates testing for the Flask To-Do List API.
# It cleans up old data, registers a new user, logs in, and then
# tests the protected to-do list endpoints.

# --- Configuration ---
BASE_URL="http://127.0.0.1:5000"
# Define a test user. Use a random number to ensure the user is unique on each run.
RANDOM_NUM=$RANDOM
TEST_USER="testuser$RANDOM_NUM"
TEST_PASS="password123"
COOKIE_FILE="cookies.txt"
DB_FILE="instance/database.db"

# --- Helper Functions ---

# Function to print a formatted header
print_header() {
    echo ""
    echo "================================================="
    echo "  $1"
    echo "================================================="
}

# --- Test Execution ---

# 1. Initial Cleanup
print_header "Step 1: Cleaning up previous session"
rm -f $COOKIE_FILE
rm -f $DB_FILE
echo "Old cookie file and database removed."
echo "Starting Flask server in the background..."
# Start the Flask app in the background and save its Process ID (PID)
python app.py &
APP_PID=$!
# Ensure the server process is killed when the script exits
trap 'echo "Stopping Flask server..."; kill $APP_PID' EXIT
# Give the server a moment to start up
sleep 2

# 2. Register a New User
print_header "Step 2: Registering a new user: $TEST_USER"
curl -X POST -H "Content-Type: application/json" \
  -d "{\"username\": \"$TEST_USER\", \"password\": \"$TEST_PASS\"}" \
  $BASE_URL/register
echo ""

# 3. Test Unauthenticated Access
print_header "Step 3: Testing API access without logging in (should fail)"
# The -i flag includes the HTTP status code in the output
curl -i $BASE_URL/api/todos
echo ""

# 4. Log In
print_header "Step 4: Logging in as $TEST_USER"
# The -c flag saves the session cookie to our file
curl -X POST -H "Content-Type: application/json" \
  -d "{\"username\": \"$TEST_USER\", \"password\": \"$TEST_PASS\"}" \
  -c $COOKIE_FILE \
  $BASE_URL/login
echo ""

# 5. Create a To-Do Item (Authenticated)
print_header "Step 5: Creating a new to-do item (authenticated)"
# The -b flag sends the cookie from our file
curl -X POST -H "Content-Type: application/json" \
  -d '{"task": "Learn how to write test scripts"}' \
  -b $COOKIE_FILE \
  $BASE_URL/api/todos
echo ""

# 6. Get To-Do List (Authenticated)
print_header "Step 6: Getting the to-do list (authenticated)"
curl -b $COOKIE_FILE $BASE_URL/api/todos
echo ""

# 7. Log Out
print_header "Step 7: Logging out"
curl -X POST -b $COOKIE_FILE $BASE_URL/logout
echo ""

# The 'trap' command will now execute and stop the server.
print_header "Test complete."
