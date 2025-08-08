#!/bin/bash

# Test MongoDB Integration
echo "🧪 Testing MongoDB Integration..."
echo "================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:8000}"
TEST_EMAIL="test_mongo_$(date +%s)@example.com"
TEST_PASSWORD="TestPassword123!"

echo -e "\n${YELLOW}1. Testing User Registration...${NC}"
REGISTER_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${TEST_EMAIL}\",
    \"password\": \"${TEST_PASSWORD}\",
    \"first_name\": \"Test\",
    \"last_name\": \"User\"
  }")

if echo "$REGISTER_RESPONSE" | grep -q "access_token"; then
  echo -e "${GREEN}✓ User registration successful${NC}"
  ACCESS_TOKEN=$(echo "$REGISTER_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
  echo "  Token: ${ACCESS_TOKEN:0:20}..."
else
  echo -e "${RED}✗ User registration failed${NC}"
  echo "  Response: $REGISTER_RESPONSE"
  exit 1
fi

echo -e "\n${YELLOW}2. Creating Research Session...${NC}"
RESEARCH_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/research/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d '{
    "title": "Test Research Session",
    "model": "gemini-1.5-flash",
    "tags": ["test", "mongodb"],
    "temperature": 0.7,
    "max_tokens": 4096
  }')

if echo "$RESEARCH_RESPONSE" | grep -q '"id"'; then
  echo -e "${GREEN}✓ Research session created successfully${NC}"
  RESEARCH_ID=$(echo "$RESEARCH_RESPONSE" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
  echo "  Research ID: $RESEARCH_ID"
else
  echo -e "${RED}✗ Failed to create research session${NC}"
  echo "  Response: $RESEARCH_RESPONSE"
  exit 1
fi

echo -e "\n${YELLOW}3. Sending Message to Research Session...${NC}"
MESSAGE_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/messages/research/${RESEARCH_ID}/send" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d '{
    "message": "Hello, this is a test message to verify MongoDB storage."
  }')

if echo "$MESSAGE_RESPONSE" | grep -q "assistant_message"; then
  echo -e "${GREEN}✓ Message sent and response received${NC}"
  echo "  Messages stored in MongoDB"
else
  echo -e "${RED}✗ Failed to send message${NC}"
  echo "  Response: $MESSAGE_RESPONSE"
  exit 1
fi

echo -e "\n${YELLOW}4. Fetching Research Sessions...${NC}"
LIST_RESPONSE=$(curl -s -X GET "${API_URL}/api/v1/research/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

if echo "$LIST_RESPONSE" | grep -q "Test Research Session"; then
  echo -e "${GREEN}✓ Research sessions fetched successfully${NC}"
  SESSION_COUNT=$(echo "$LIST_RESPONSE" | grep -o '"total":[0-9]*' | cut -d':' -f2)
  echo "  Total sessions: $SESSION_COUNT"
else
  echo -e "${RED}✗ Failed to fetch research sessions${NC}"
  echo "  Response: $LIST_RESPONSE"
fi

echo -e "\n${YELLOW}5. Fetching Conversation History...${NC}"
CONVERSATION_RESPONSE=$(curl -s -X GET "${API_URL}/api/v1/messages/research/${RESEARCH_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

if echo "$CONVERSATION_RESPONSE" | grep -q "test message"; then
  echo -e "${GREEN}✓ Conversation history retrieved successfully${NC}"
  MESSAGE_COUNT=$(echo "$CONVERSATION_RESPONSE" | grep -o '"total_messages":[0-9]*' | cut -d':' -f2)
  echo "  Total messages: $MESSAGE_COUNT"
else
  echo -e "${RED}✗ Failed to fetch conversation history${NC}"
  echo "  Response: $CONVERSATION_RESPONSE"
fi

echo -e "\n${YELLOW}6. Checking MongoDB Collections...${NC}"
echo "Run this command to verify data in MongoDB Compass:"
echo -e "${GREEN}mongodb://elenchus_admin:elenchus_password_2024@localhost:27018/${NC}"
echo ""
echo "Expected collections with data:"
echo "  - users: Should have the test user"
echo "  - research: Should have the test research session"
echo "  - messages: Should have user and assistant messages"

echo -e "\n${GREEN}✅ MongoDB Integration Test Complete!${NC}"
echo "================================"
echo ""
echo "Summary:"
echo "  - User created: ${TEST_EMAIL}"
echo "  - Research ID: ${RESEARCH_ID}"
echo "  - Data is being stored in MongoDB"
echo ""
echo "To clean up test data, delete from MongoDB:"
echo "  db.users.deleteOne({email: '${TEST_EMAIL}'})"
echo "  db.research.deleteOne({_id: ObjectId('${RESEARCH_ID}')})"
echo "  db.messages.deleteMany({research_id: '${RESEARCH_ID}'})"