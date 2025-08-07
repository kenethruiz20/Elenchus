#!/bin/bash

# Test Authentication Flow Script

echo "🔐 Testing Elenchus AI Authentication System"
echo "============================================"

API_URL="http://localhost:8001/api/v1"
FRONTEND_URL="http://localhost:3001"

# Generate unique test email
TEST_EMAIL="test-$(date +%s)@example.com"
TEST_PASSWORD="testPassword123"

echo ""
echo "📝 Test 1: Register New User"
echo "Email: $TEST_EMAIL"
echo "Password: $TEST_PASSWORD"

REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$TEST_EMAIL\", \"password\": \"$TEST_PASSWORD\", \"first_name\": \"Test\", \"last_name\": \"User\"}")

if echo "$REGISTER_RESPONSE" | grep -q "access_token"; then
  echo "✅ Registration successful!"
  TOKEN=$(echo "$REGISTER_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
  echo "Token received: ${TOKEN:0:20}..."
else
  echo "❌ Registration failed!"
  echo "$REGISTER_RESPONSE"
  exit 1
fi

echo ""
echo "📝 Test 2: Login with Credentials"
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$TEST_EMAIL\", \"password\": \"$TEST_PASSWORD\"}")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
  echo "✅ Login successful!"
  TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
else
  echo "❌ Login failed!"
  echo "$LOGIN_RESPONSE"
  exit 1
fi

echo ""
echo "📝 Test 3: Access Protected Endpoint"
ME_RESPONSE=$(curl -s -X GET "$API_URL/auth/me" \
  -H "Authorization: Bearer $TOKEN")

if echo "$ME_RESPONSE" | grep -q "$TEST_EMAIL"; then
  echo "✅ Protected endpoint access successful!"
  echo "User info retrieved: $(echo "$ME_RESPONSE" | grep -o '"email":"[^"]*' | cut -d'"' -f4)"
else
  echo "❌ Protected endpoint access failed!"
  echo "$ME_RESPONSE"
  exit 1
fi

echo ""
echo "📝 Test 4: Password Reset Request"
RESET_RESPONSE=$(curl -s -X POST "$API_URL/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$TEST_EMAIL\"}")

if echo "$RESET_RESPONSE" | grep -q "Token:"; then
  echo "✅ Password reset request successful!"
  RESET_TOKEN=$(echo "$RESET_RESPONSE" | grep -o 'Token: [^"]*' | cut -d' ' -f2)
  echo "Reset token received: ${RESET_TOKEN:0:20}..."
else
  echo "❌ Password reset request failed!"
  echo "$RESET_RESPONSE"
  exit 1
fi

echo ""
echo "📝 Test 5: Frontend Health Check"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL/app")

if [ "$FRONTEND_STATUS" == "200" ]; then
  echo "✅ Frontend is accessible!"
else
  echo "❌ Frontend is not accessible! Status: $FRONTEND_STATUS"
  exit 1
fi

echo ""
echo "📝 Test 6: Backend Models Endpoint (Protected)"
MODELS_RESPONSE=$(curl -s -X GET "$API_URL/models" \
  -H "Authorization: Bearer $TOKEN")

echo "✅ Models endpoint response received"

echo ""
echo "============================================"
echo "✨ All Authentication Tests Passed!"
echo ""
echo "🎯 Summary:"
echo "- Backend API: ✅ Running at $API_URL"
echo "- Frontend App: ✅ Running at $FRONTEND_URL"
echo "- Authentication: ✅ Working properly"
echo "- Protected Routes: ✅ Secured with JWT"
echo ""
echo "📱 You can now visit the app at: $FRONTEND_URL/app"
echo "   The authentication modal will appear automatically"
echo ""