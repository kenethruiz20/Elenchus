// MongoDB initialization script for Elenchus Legal AI
// This script runs when the MongoDB container starts for the first time

// Switch to elenchus database
db = db.getSiblingDB('elenchus');

// Create application user
db.createUser({
    user: 'elenchus_user',
    pwd: 'elenchus_app_password',
    roles: [
        {
            role: 'readWrite',
            db: 'elenchus'
        }
    ]
});

// Create collections with initial indexes
db.createCollection('users');
db.createCollection('conversations');
db.createCollection('messages');
db.createCollection('documents');
db.createCollection('workflows');
db.createCollection('analytics');

// Create indexes for better performance
// Users collection indexes
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "google_id": 1 }, { unique: true, sparse: true });
db.users.createIndex({ "created_at": 1 });

// Conversations collection indexes
db.conversations.createIndex({ "user_id": 1 });
db.conversations.createIndex({ "session_id": 1 }, { unique: true });
db.conversations.createIndex({ "created_at": -1 });
db.conversations.createIndex({ "user_id": 1, "is_active": 1 });

// Messages collection indexes
db.messages.createIndex({ "conversation_id": 1 });
db.messages.createIndex({ "conversation_id": 1, "created_at": 1 });
db.messages.createIndex({ "trace_id": 1 });
db.messages.createIndex({ "created_at": -1 });

// Documents collection indexes
db.documents.createIndex({ "user_id": 1 });
db.documents.createIndex({ "content_hash": 1 });
db.documents.createIndex({ "processing_status": 1 });
db.documents.createIndex({ "user_id": 1, "created_at": -1 });
db.documents.createIndex({ "document_category": 1 });

// Workflows collection indexes
db.workflows.createIndex({ "user_id": 1 });
db.workflows.createIndex({ "execution_id": 1 }, { unique: true });
db.workflows.createIndex({ "status": 1 });
db.workflows.createIndex({ "user_id": 1, "created_at": -1 });

// Analytics collection indexes
db.analytics.createIndex({ "user_id": 1, "date": 1 }, { unique: true });
db.analytics.createIndex({ "date": -1 });

print('✅ Elenchus database initialized successfully');
print('✅ Collections created: users, conversations, messages, documents, workflows, analytics');
print('✅ Indexes created for optimal performance');
print('✅ Application user created: elenchus_user');