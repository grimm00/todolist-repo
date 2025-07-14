#!/bin/bash

# This script runs a sequence of curl commands to test the API.
# It assumes that the Flask application is already running.

# --- Configuration ---
BASE_URL="http://127.0.0.1:5000"
# Define a test user. Use a random number to make it unique.
RANDOM_NUM=$RANDOM
TEST_USER="testuser$RANDOM_NUM"
TEST_PASS="password123"
COOKIE_FILE="cookies.txt"

# --- Helper Functions ---

# Function to print a formatted header
print_header() {
    echo ""
    echo "--- $1 ---"
}

# --- Test Execution ---

# 1. Register a New User
print_header "Step 1: Registering a new user: $TEST_USER"
curl -X POST -H "Content-Type: application/json" \
  -d "{\"username\": \"$TEST_USER\", \"password\": \"$TEST_PASS\"}" \
  $BASE_URL/register
echo ""

# 2. Test Unauthenticated Access
print_header "Step 2: Testing API access without logging in (should fail with 401)"
# The -i flag includes the HTTP status code in the output
curl -i $BASE_URL/api/todos
echo ""

# 3. Log In
print_header "Step 3: Logging in as $TEST_USER"
# The -c flag saves the session cookie to our file
curl -X POST -H "Content-Type: application/json" \
  -d "{\"username\": \"$TEST_USER\", \"password\": \"$TEST_PASS\"}" \
  -c $COOKIE_FILE \
  $BASE_URL/login
echo ""

# 4. Create a To-Do Item (Authenticated)
print_header "Step 4: Creating a new to-do item (authenticated)"
# The -b flag sends the cookie from our file
curl -X POST -H "Content-Type: application/json" \
  -d '{"task": "Learn how to write test scripts"}' \
  -b $COOKIE_FILE \
  $BASE_URL/api/todos
echo ""

# 5. Get To-Do List (Authenticated)
print_header "Step 5: Getting the to-do list (authenticated)"
curl -b $COOKIE_FILE $BASE_URL/api/todos
echo ""

# 6. Log Out
print_header "Step 6: Logging out"
curl -X POST -b $COOKIE_FILE $BASE_URL/logout
echo ""

# 7. Cleanup
print_header "Step 7: Cleaning up"
rm -f $COOKIE_FILE
echo "Cookie file removed."
echo ""
echo "✅ Test script complete."
