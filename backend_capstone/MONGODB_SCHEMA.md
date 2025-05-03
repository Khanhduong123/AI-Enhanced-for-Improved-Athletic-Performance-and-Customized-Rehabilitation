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
  "_id": ObjectId,
  "email": String,
  "full_name": String,
  "role": String,  // "Doctor" or "Patient"
  "hashed_password": String,
  "created_at": DateTime,
  "updated_at": DateTime
}
```

**Indexes**:

- `email`: Unique index for fast user lookup by email
- `role`: Index for filtering users by role

**Security Considerations**:

- Passwords are hashed and never stored in plain text
- Role field provides basis for access control

### 2. Exercises Collection

**Purpose**: Track exercises assigned by doctors to patients

**Schema**:

```json
{
  "_id": ObjectId,
  "name": String,
  "description": String,
  "assigned_by": ObjectId,  // Reference to doctor user
  "assigned_to": ObjectId,  // Reference to patient user
  "assigned_date": DateTime,
  "due_date": DateTime,
  "status": String,  // "Pending", "Completed", "Not Completed"
  "created_at": DateTime,
  "updated_at": DateTime
}
```

**Indexes**:

- `assigned_by`: Index for fast retrieval of exercises by doctor
- `assigned_to`: Index for fast retrieval of exercises by patient
- `status`: Index for filtering exercises by status
- `assigned_date`: Index for time-based queries
- Compound index `{assigned_to, assigned_date}`: For patient exercise history

### 3. Videos Collection

**Purpose**: Store metadata about uploaded exercise videos

**Schema**:

```json
{
  "_id": ObjectId,
  "patient_id": ObjectId,  // Reference to patient user
  "exercise_id": ObjectId,  // Reference to exercise
  "file_path": String,      // Path to stored video file
  "file_name": String,
  "file_size": Number,      // Size in bytes
  "content_type": String,   // MIME type
  "upload_date": DateTime,
  "status": String,         // "Uploaded", "Procsesed", "Failed"
  "created_at": DateTime,
  "updated_at": DateTime
}
```

**Indexes**:

- `patient_id`: Index for retrieving videos by patient
- `exercise_id`: Index for retrieving videos by exercise
- `upload_date`: Index for time-based queries
- Compound index `{exercise_id, upload_date}`: For exercise video history

### 4. Predictions Collection

**Purpose**: Store AI predictions for exercise videos

**Schema**:

```json
{
  "_id": ObjectId,
  "video_id": ObjectId,     // Reference to video
  "exercise_id": ObjectId,  // Reference to exercise
  "patient_id": ObjectId,   // Reference to patient user
  "predicted_motion": String,
  "confidence_score": Number, // 0-1 range
  "is_match": Boolean,      // Whether prediction matches exercise
  "model_name": String,     // AI model used
  "status": String,         // "Completed", "Not Completed", "Pending", "Failed"
  "raw_results": Object,    // Raw AI model output
  "feedback": String,       // Optional doctor feedback
  "feedback_date": DateTime, // When feedback was provided
  "created_at": DateTime,
  "updated_at": DateTime
}
```

**Indexes**:

- `video_id`: Unique index for one-to-one relationship with videos
- `patient_id`: Index for retrieving predictions by patient
- `exercise_id`: Index for retrieving predictions by exercise
- `created_at`: Index for time-based queries
- `status`: Index for filtering by prediction status
- Compound index `{patient_id, created_at}`: For patient prediction history
- Compound index `{exercise_id, created_at}`: For exercise prediction history

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
   - Passwords hashed for security
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
