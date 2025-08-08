#!/bin/bash

# Test Messages Fix - MongoDB ObjectId Issue
echo "🧪 Testing Messages Fix..."
echo "================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:8000}"
TEST_EMAIL="test_messages_$(date +%s)@example.com"
TEST_PASSWORD="TestPassword123!"

echo -e "\n${YELLOW}1. Creating Test User...${NC}"
REGISTER_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${TEST_EMAIL}\",
    \"password\": \"${TEST_PASSWORD}\",
    \"first_name\": \"Messages\",
    \"last_name\": \"Test\"
  }")

if echo "$REGISTER_RESPONSE" | grep -q "access_token"; then
  echo -e "${GREEN}✓ User created${NC}"
  ACCESS_TOKEN=$(echo "$REGISTER_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
else
  echo -e "${RED}✗ Failed to create user${NC}"
  echo "  Response: $REGISTER_RESPONSE"
  exit 1
fi

echo -e "\n${YELLOW}2. Creating Research Session (Backend returns ObjectId)...${NC}"
RESEARCH_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/research/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d '{
    "title": "ObjectId Test Session",
    "model": "gemini-1.5-flash",
    "tags": ["test"],
    "temperature": 0.7,
    "max_tokens": 4096
  }')

if echo "$RESEARCH_RESPONSE" | grep -q '"id"'; then
  RESEARCH_ID=$(echo "$RESEARCH_RESPONSE" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
  echo -e "${GREEN}✓ Research session created${NC}"
  echo "  Backend ObjectId: $RESEARCH_ID"
  echo "  ID Length: ${#RESEARCH_ID} characters (should be 24 for ObjectId)"
  
  # Verify it's a valid ObjectId format (24 hex characters)
  if [[ $RESEARCH_ID =~ ^[a-f0-9]{24}$ ]]; then
    echo -e "${GREEN}  ✓ Valid MongoDB ObjectId format${NC}"
  else
    echo -e "${RED}  ✗ Invalid ObjectId format!${NC}"
  fi
else
  echo -e "${RED}✗ Failed to create research session${NC}"
  echo "  Response: $RESEARCH_RESPONSE"
  exit 1
fi

echo -e "\n${YELLOW}3. Sending Message with ObjectId...${NC}"
MESSAGE_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/messages/research/${RESEARCH_ID}/send" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d '{
    "message": "Hi! My name is Alex. This is a test of the ObjectId fix."
  }')

if echo "$MESSAGE_RESPONSE" | grep -q "assistant_message"; then
  echo -e "${GREEN}✓ Message sent successfully!${NC}"
  ASSISTANT_MSG=$(echo "$MESSAGE_RESPONSE" | grep -o '"content":"[^"]*' | head -1 | cut -d'"' -f4)
  echo "  Assistant replied: ${ASSISTANT_MSG:0:50}..."
else
  echo -e "${RED}✗ Failed to send message${NC}"
  echo "  Response: $MESSAGE_RESPONSE"
  
  # Check if it's the ObjectId error
  if echo "$MESSAGE_RESPONSE" | grep -q "not a valid ObjectId"; then
    echo -e "${RED}  ERROR: Still getting ObjectId validation error!${NC}"
    echo "  The backend is still rejecting the ID format"
  fi
fi

echo -e "\n${YELLOW}4. Fetching Conversation to Verify Storage...${NC}"
CONVERSATION_RESPONSE=$(curl -s -X GET "${API_URL}/api/v1/messages/research/${RESEARCH_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

if echo "$CONVERSATION_RESPONSE" | grep -q "Alex"; then
  echo -e "${GREEN}✓ Messages are being stored and retrieved!${NC}"
  MESSAGE_COUNT=$(echo "$CONVERSATION_RESPONSE" | grep -o '"total_messages":[0-9]*' | cut -d':' -f2)
  echo "  Total messages in conversation: $MESSAGE_COUNT"
else
  echo -e "${YELLOW}⚠ Could not verify message storage${NC}"
  echo "  Response: ${CONVERSATION_RESPONSE:0:100}..."
fi

echo -e "\n${GREEN}✅ Test Complete!${NC}"
echo "================================"
echo ""
echo "Summary:"
echo "  Research ID Format: MongoDB ObjectId (24 hex chars)"
echo "  Research ID: ${RESEARCH_ID}"
echo "  Messages endpoint: /api/v1/messages/research/${RESEARCH_ID}/send"
echo ""
echo "The fix should now:"
echo "  1. Create research sessions with MongoDB ObjectIds"
echo "  2. Use the ObjectId for all message operations"
echo "  3. Store messages properly in MongoDB"