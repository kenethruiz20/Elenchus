#!/bin/bash

echo "Testing upload with background processing..."

# Create a test document
TEST_FILE="/tmp/test_business_plan.txt"
cat > "$TEST_FILE" << 'EOF'
BUSINESS PLAN: TECH STARTUP

Executive Summary:
We are launching a revolutionary AI-powered document management platform that will transform how businesses handle their paperwork.

Market Opportunity:
The global document management market is valued at $5.1 billion and growing at 12% annually. Our target market includes small to medium businesses seeking digital transformation.

Product Description:
Our platform uses artificial intelligence to automatically categorize, summarize, and extract key insights from business documents. Key features include:
- Intelligent document classification
- AI-powered content extraction
- Automated workflow integration
- Enterprise-grade security

Financial Projections:
Year 1: $250K revenue (500 customers)
Year 2: $850K revenue (1,500 customers)
Year 3: $2.1M revenue (3,200 customers)

Implementation Timeline:
Q1 2025: MVP development and beta testing
Q2 2025: Public launch and customer acquisition
Q3-Q4 2025: Feature expansion and market growth

Team:
Our founding team has 15+ years combined experience in AI, software development, and business operations.
EOF

echo "Created test file: $TEST_FILE"

# Login and get token
echo "1. Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPassword123!"}')

TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['token']['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed!"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

echo "✅ Login successful"

# Upload document
echo "2. Uploading document..."
UPLOAD_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST http://localhost:8000/api/v1/rag/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@$TEST_FILE" \
  -F 'tags=["business-plan", "startup"]' \
  -F "category=planning")

HTTP_STATUS=$(echo "$UPLOAD_RESPONSE" | grep "HTTP_STATUS:" | sed 's/HTTP_STATUS://')
RESPONSE_BODY=$(echo "$UPLOAD_RESPONSE" | sed '/HTTP_STATUS:/d')

echo "   Upload status: $HTTP_STATUS"

if [ "$HTTP_STATUS" = "200" ]; then
  echo "✅ Upload successful!"
  
  # Extract document ID
  DOC_ID=$(echo "$RESPONSE_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
  
  if [ -n "$DOC_ID" ]; then
    echo "   Document ID: $DOC_ID"
    
    # Wait for background processing
    echo "3. Waiting for background processing (30 seconds)..."
    sleep 30
    
    # Check document status
    echo "4. Checking document status..."
    STATUS_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/rag/documents/$DOC_ID/status" \
      -H "Authorization: Bearer $TOKEN")
    
    echo "   Status response: $STATUS_RESPONSE"
    
    # Try to download
    echo "5. Testing download..."
    DOWNLOAD_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X GET "http://localhost:8000/api/v1/rag/documents/$DOC_ID/download" \
      -H "Authorization: Bearer $TOKEN" \
      -o "/tmp/downloaded_test.txt")
    
    DOWNLOAD_STATUS=$(echo "$DOWNLOAD_RESPONSE" | grep "HTTP_STATUS:" | sed 's/HTTP_STATUS://')
    echo "   Download status: $DOWNLOAD_STATUS"
    
    if [ "$DOWNLOAD_STATUS" = "200" ]; then
      echo "✅ Download successful!"
      echo "   Downloaded file size: $(wc -c < /tmp/downloaded_test.txt) bytes"
    else
      echo "❌ Download failed"
    fi
  fi
  
else
  echo "❌ Upload failed!"
  echo "Response: $RESPONSE_BODY"
fi

# Cleanup
rm -f "$TEST_FILE" "/tmp/downloaded_test.txt"