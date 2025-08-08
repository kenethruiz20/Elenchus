/**
 * Test script for RAG file upload integration
 * This script tests the complete flow: login -> upload file -> check status
 */

const API_BASE_URL = 'http://localhost:8000';

// Test user credentials (create these in your backend if they don't exist)
const TEST_USER = {
  email: 'test@example.com',
  password: 'testpassword123'
};

async function testRagUpload() {
  console.log('🔄 Starting RAG Upload Integration Test...\n');

  try {
    // Step 1: Login to get auth token
    console.log('1. Logging in...');
    const loginResponse = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: TEST_USER.email,
        password: TEST_USER.password
      })
    });

    if (!loginResponse.ok) {
      const error = await loginResponse.text();
      throw new Error(`Login failed: ${loginResponse.status} - ${error}`);
    }

    const loginData = await loginResponse.json();
    const token = loginData.token?.access_token || loginData.access_token;
    console.log('✅ Login successful');
    console.log(`   Token: ${token?.substring(0, 20)}...`);

    // Step 2: Test RAG endpoints availability
    console.log('\n2. Testing RAG endpoint availability...');
    const ragTestResponse = await fetch(`${API_BASE_URL}/api/v1/rag/documents`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!ragTestResponse.ok) {
      const error = await ragTestResponse.text();
      console.log(`⚠️  RAG endpoint response: ${ragTestResponse.status} - ${error}`);
    } else {
      const ragData = await ragTestResponse.json();
      console.log('✅ RAG endpoint accessible');
      console.log(`   Found ${ragData.documents ? ragData.documents.length : 0} existing documents`);
    }

    // Step 3: Create a test file
    console.log('\n3. Creating test file...');
    const testContent = `
# Test Document for RAG Integration

This is a test document to verify the RAG upload functionality.

## Key Points:
- The file upload should work through the frontend
- The document should be stored in MongoDB
- The file should be uploaded to GCS
- The document should be available for RAG processing

## Test Data:
- Date: ${new Date().toISOString()}
- Test ID: ${Math.random().toString(36).substring(2, 15)}

This document contains important legal information for testing purposes.
    `.trim();

    // Create a Blob that mimics a text file
    const testBlob = new Blob([testContent], { type: 'text/plain' });
    const testFile = new File([testBlob], 'test-document.txt', { type: 'text/plain' });

    // Step 4: Upload the file
    console.log('\n4. Uploading test file...');
    const formData = new FormData();
    formData.append('file', testFile);

    const uploadResponse = await fetch(`${API_BASE_URL}/api/v1/rag/documents/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });

    if (!uploadResponse.ok) {
      const error = await uploadResponse.text();
      console.error(`❌ Upload failed: ${uploadResponse.status} - ${error}`);
      return;
    }

    const uploadData = await uploadResponse.json();
    console.log('✅ File uploaded successfully');
    console.log('   Response:', JSON.stringify(uploadData, null, 2));
    
    if (uploadData.document) {
      console.log(`   Document ID: ${uploadData.document.id}`);
      console.log(`   Status: ${uploadData.document.status}`);
      console.log(`   File size: ${uploadData.document.file_size} bytes`);
      console.log(`   GCS path: ${uploadData.document.gcs_path}`);
    }

    // Step 5: Verify document in list
    console.log('\n5. Verifying document in list...');
    const listResponse = await fetch(`${API_BASE_URL}/api/v1/rag/documents`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (listResponse.ok) {
      const listData = await listResponse.json();
      const uploadedDoc = listData.documents.find(doc => doc.id === uploadData.document.id);
      if (uploadedDoc) {
        console.log('✅ Document found in list');
        console.log(`   Status: ${uploadedDoc.status}`);
      } else {
        console.log('❌ Document not found in list');
      }
    }

    console.log('\n🎉 RAG Upload Integration Test Completed Successfully!');
    console.log('\n📋 Next Steps:');
    console.log('   • The frontend should now be able to upload files');
    console.log('   • Files will be stored in GCS and MongoDB');
    console.log('   • Ready for Stage 5: Background Worker & Task Queue');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.log('\n🔧 Troubleshooting:');
    console.log('   • Make sure the backend is running (devrun.sh)');
    console.log('   • Ensure test user exists or create one');
    console.log('   • Check that GCS credentials are configured');
  }
}

// Run the test
testRagUpload().catch(console.error);