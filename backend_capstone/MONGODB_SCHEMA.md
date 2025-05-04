# MongoDB Schema Design

This document outlines the MongoDB schema design for the exercise prediction application. It provides details on collections, indexes, relationships, and performance considerations.

## Collections Overview

The database is organized into four main collections, each with specific purposes and relationships:

1. **users** - Stores user information for both patients and doctors
2. **exercises** - Stores exercise assignments from doctors to patients
3. **videos** - Stores metadata about uploaded exercise videos
4. **predictions** - Stores AI prediction results for exercise videos

## Collection Details

### 1. Users Collection

**Purpose**: Store user accounts with role-based access control (doctor/patient)

**Schema**:

```json
{
  "_id": String,           // User ID (string, not ObjectId)
  "email": String,         // User's email (unique)
  "full_name": String,     // User's full name
  "role": String,          // "Doctor" or "Patient" (case-insensitive, may have typo in legacy data)
  "hashed_password": String, // SHA-256 hash of password
  "created_at": Date,
  "updated_at": Date
}
```

**Indexes**:

- `email` (unique)
- `role`
- `created_at`

### 2. Exercises Collection

**Purpose**: Track exercises assigned by doctors to patients

**Schema**:

```json
{
  "_id": String,             // Exercise ID (string, not ObjectId)
  "name": String,            // Exercise name
  "description": String,     // Exercise description
  "assigned_by": String,     // User ID of doctor (string)
  "assigned_to": String,     // User ID of patient (string)
  "assigned_date": Date,
  "due_date": Date,
  "status": String,          // "Pending", "Completed", "Not Completed"
  "created_at": Date,
  "updated_at": Date
}
```

**Indexes**:

- `assigned_by`
- `assigned_to`
- `status`
- `assigned_date`
- Compound: `{assigned_to, assigned_date}`

### 3. Videos Collection

**Purpose**: Store metadata about uploaded exercise videos

**Schema**:

```json
{
  "_id": String,             // Video ID (string, not ObjectId)
  "patient_id": String,      // User ID of patient (string)
  "exercise_id": String,     // Exercise ID (string)
  "file_path": String,       // Path to stored video file
  "file_name": String,
  "file_size": Number,
  "content_type": String,
  "upload_date": Date,
  "status": String,          // "Uploaded", "Processed", "Failed"
  "created_at": Date,
  "updated_at": Date
}
```

**Indexes**:

- `patient_id`
- `exercise_id`
- `upload_date`
- Compound: `{exercise_id, upload_date}`

### 4. Predictions Collection

**Purpose**: Store AI predictions for exercise videos

**Schema**:

```json
{
  "_id": String,             // Prediction ID (string, not ObjectId)
  "video_id": String,        // Video ID (string)
  "exercise_id": String,     // Exercise ID (string)
  "patient_id": String,      // User ID of patient (string)
  "predicted_motion": String,// AI-predicted motion label
  "confidence_score": Number,// Float in [0, 1]
  "is_match": Boolean,       // Whether prediction matches assigned exercise
  "model_name": String,      // Name of AI model used
  "status": String,          // "Completed", "Not Completed", "Pending", "Failed"
  "raw_results": Object,     // Raw AI model output (dict)
  "feedback": String,        // Optional doctor feedback
  "feedback_date": Date,     // When feedback was provided
  "created_at": Date,
  "updated_at": Date
}
```

**Indexes**:

- `video_id` (unique)
- `patient_id`
- `exercise_id`
- `created_at`
- `status`
- Compound: `{patient_id, created_at}`
- Compound: `{exercise_id, created_at}`

## Relationships

The MongoDB schema uses a referenced approach (normalized) for relationships between entities:

1. **User → Exercise** (One-to-Many)

   - Doctor assigns exercises to patients
   - Exercise record contains references to both doctor (`assigned_by`) and patient (`assigned_to`)

2. **Exercise → Video** (One-to-Many)

   - Exercise can have multiple videos
   - Video record contains reference to exercise (`exercise_id`)

3. **Video → Prediction** (One-to-One)

   - Each video has exactly one prediction
   - Prediction record contains reference to video (`video_id`)

4. **Patient → Video** (One-to-Many)

   - Patient can upload multiple videos
   - Video record contains reference to patient (`patient_id`)

5. **Patient → Prediction** (One-to-Many)
   - Patient has multiple predictions through videos
   - Prediction record contains reference to patient (`patient_id`)

## Performance Considerations

1. **Indexing Strategy**:

   - Indexes on all frequently queried fields
   - Compound indexes for common query patterns
   - Background index creation to avoid blocking operations

2. **Query Optimization**:

   - Pagination implemented on all list endpoints
   - Filtering capabilities to reduce result sets
   - Projection used to return only needed fields

3. **Data Volume Management**:
   - Video files stored on filesystem, metadata in database
   - Raw prediction results can be optionally excluded from responses

## Security Considerations

1. **Data Access Control**:

   - Role-based access (Doctor/Patient)
   - Users can only access their own data or data explicitly shared with them
   - Doctors can only see data for patients assigned to them

2. **Data Encryption**:
   - Passwords hashed using SHA-256
   - Environment variables for sensitive configuration

## Design Decisions

1. **Normalized vs. Denormalized**:

   - Chose normalized approach (using references) for data integrity
   - Prevents data duplication and ensures consistency
   - Application layer handles combining data when needed

2. **Indexing Strategy**:

   - Carefully selected indexes to optimize common queries
   - Balanced between query performance and index maintenance overhead

3. **Datetime Fields**:
   - Consistent use of created_at/updated_at fields for auditing
   - Specific date fields for domain-relevant timestamps

## MongoDB ERD (Entity-Relationship Diagram)

```
┌─────────────┐       ┌───────────────┐        ┌─────────────┐      ┌────────────────┐
│   Users     │       │   Exercises   │        │   Videos    │      │   Predictions  │
├─────────────┤       ├───────────────┤        ├─────────────┤      ├────────────────┤
│ _id         │       │ _id           │        │ _id         │      │ _id            │
│ email       │       │ name          │        │ patient_id  │──┐   │ video_id       │──┐
│ full_name   │       │ description   │        │ exercise_id │──┼──>│ exercise_id    │  │
│ role        │<──┐   │ assigned_by   │<─┐     │ file_path   │  │   │ patient_id     │<─┘
│ hashed_pwd  │   │   │ assigned_to   │──┼────>│ file_name   │  └──>│ predicted_motion│
│ created_at  │   └───│ assigned_date │  │     │ file_size   │      │ confidence_score│
│ updated_at  │       │ due_date      │  │     │ content_type│      │ is_match       │
└─────────────┘       │ status        │  │     │ upload_date │      │ model_name     │
                      │ created_at    │  │     │ status      │      │ status         │
                      │ updated_at    │  │     │ created_at  │      │ raw_results    │
                      └───────────────┘  │     │ updated_at  │      │ feedback       │
                                         │     └─────────────┘      │ feedback_date  │
                                         │                          │ created_at     │
                                         │                          │ updated_at     │
                                         └─────────────────────────>└────────────────┘
```
