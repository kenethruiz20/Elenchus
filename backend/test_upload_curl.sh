#!/bin/bash

echo "Testing RAG document upload without email verification..."
echo ""

# First login to get token
echo "1. Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPassword123!"}')

# Extract token using grep and sed
TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed!"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

echo "✅ Login successful"

# Check if user is verified
IS_VERIFIED=$(echo "$LOGIN_RESPONSE" | grep -o '"is_verified":[^,}]*' | sed 's/"is_verified"://')
echo "   User verified status: $IS_VERIFIED"
echo ""

# Create a test file
TEST_FILE="/tmp/test_document.txt"
echo "This is a test document for RAG upload without email verification." > "$TEST_FILE"

# Upload document
echo "2. Uploading document..."
UPLOAD_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST http://localhost:8000/api/v1/rag/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@$TEST_FILE" \
  -F 'tags=["test", "no-verification"]' \
  -F "category=test")

# Extract HTTP status code
HTTP_STATUS=$(echo "$UPLOAD_RESPONSE" | grep "HTTP_STATUS:" | sed 's/HTTP_STATUS://')
RESPONSE_BODY=$(echo "$UPLOAD_RESPONSE" | sed '/HTTP_STATUS:/d')

echo "   Upload status: $HTTP_STATUS"
echo ""

if [ "$HTTP_STATUS" = "200" ]; then
  echo "✅ Upload successful!"
  echo "Response: $RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
else
  echo "❌ Upload failed!"
  echo "Response: $RESPONSE_BODY"
  
  if echo "$RESPONSE_BODY" | grep -q "Email not verified"; then
    echo ""
    echo "⚠️  ISSUE: Email verification is still being required!"
    echo "   The authentication dependency needs to be checked."
  fi
fi

# Clean up
rm -f "$TEST_FILE"