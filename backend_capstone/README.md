# Exercise Tracker Backend

This is a FastAPI-based backend for an exercise tracking application that uses AI to analyze patient exercise videos.

## Features

- User Management (Doctors and Patients)
- Exercise Assignment
- Video Upload and Processing
- AI-powered Motion Analysis
- Progress Tracking

## Tech Stack

- FastAPI: High-performance web framework
- MongoDB: NoSQL database for flexible schema
- Motor: Async MongoDB driver
- Pydantic: Data validation
- Python 3.8+

## Setup Instructions

### Prerequisites

- Python 3.8+
- MongoDB

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
MONGO_URI=mongodb://localhost:27017
DB_NAME=exercise_tracker_db
```

### Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:7860`

## API Documentation

Once the server is running, you can access the interactive API documentation at:

- Swagger UI: `http://localhost:7860/docs`
- ReDoc: `http://localhost:7860/redoc`

## Database Schema

### Users Collection

Stores information about doctors and patients:

- `_id`: ObjectId (Unique identifier)
- `email`: String (Unique email address)
- `full_name`: String
- `role`: String ("Doctor" or "Patient")
- `hashed_password`: String
- `created_at`: DateTime
- `updated_at`: DateTime

### Exercises Collection

Stores exercise assignments:

- `_id`: ObjectId (Unique identifier)
- `name`: String (Exercise name)
- `description`: String
- `assigned_by`: ObjectId (Reference to doctor)
- `assigned_to`: ObjectId (Reference to patient)
- `assigned_date`: DateTime
- `due_date`: DateTime (Optional)
- `status`: String ("Pending", "Completed", "Not Completed")
- `created_at`: DateTime
- `updated_at`: DateTime

### Videos Collection

Stores information about uploaded videos:

- `_id`: ObjectId (Unique identifier)
- `patient_id`: ObjectId (Reference to patient)
- `exercise_id`: ObjectId (Reference to exercise)
- `file_path`: String (Path to video file)
- `file_name`: String
- `file_size`: Number (File size in bytes)
- `content_type`: String (MIME type)
- `upload_date`: DateTime
- `status`: String ("Uploaded", "Processed", "Failed")
- `created_at`: DateTime
- `updated_at`: DateTime

### Predictions Collection

Stores AI predictions:

- `_id`: ObjectId (Unique identifier)
- `video_id`: ObjectId (Reference to video)
- `exercise_id`: ObjectId (Reference to exercise)
- `patient_id`: ObjectId (Reference to patient)
- `predicted_motion`: String
- `confidence_score`: Number (0-1)
- `model_name`: String
- `is_match`: Boolean
- `raw_results`: Object
- `created_at`: DateTime

## API Endpoints

### User Management

- `POST /api/v1/users/`: Register a new user
- `POST /api/v1/users/login`: Login
- `GET /api/v1/users/{user_id}`: Get user profile
- `PUT /api/v1/users/{user_id}`: Update user profile

### Exercise Management

- `POST /api/v1/exercises/`: Create a new exercise
- `GET /api/v1/exercises/{exercise_id}`: Get exercise details
- `PUT /api/v1/exercises/{exercise_id}`: Update exercise
- `GET /api/v1/exercises/patient/{patient_id}`: Get patient's exercises
- `GET /api/v1/exercises/doctor/{doctor_id}`: Get doctor's assigned exercises

### Video Management

- `POST /api/v1/predict/`: Upload and analyze a video
- `GET /api/v1/videos/{video_id}`: Get video with prediction
- `GET /api/v1/videos/patient/{patient_id}`: Get patient's videos
- `GET /api/v1/predict/exercise/{exercise_id}/videos`: Get videos for an exercise

## License

MIT