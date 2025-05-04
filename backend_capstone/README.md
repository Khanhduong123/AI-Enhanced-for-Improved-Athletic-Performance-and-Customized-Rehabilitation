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

### User Endpoints

- `POST /api/v1/users/register` - Register new user
- `POST /api/v1/users/login` - User login
- `GET /api/v1/users/me` - Get current user info
- `GET /api/v1/users/` - List users (with pagination)
- `GET /api/v1/users/{user_id}` - Get specific user

### Exercise Endpoints

- `POST /api/v1/exercises/` - Create new exercise
- `GET /api/v1/exercises/` - List exercises (with pagination)
- `GET /api/v1/exercises/{exercise_id}` - Get specific exercise
- `GET /api/v1/exercises/patient/{patient_id}` - Get patient's exercises
- `GET /api/v1/exercises/doctor/{doctor_id}` - Get doctor's assigned exercises

### Video Endpoints

- `POST /api/v1/videos/upload` - Upload exercise video
- `GET /api/v1/videos/` - List videos (with pagination)
- `GET /api/v1/videos/{video_id}` - Get specific video
- `GET /api/v1/videos/exercise/{exercise_id}` - Get videos for exercise
- `GET /api/v1/videos/patient/{patient_id}` - Get patient's videos

### Prediction Endpoints

- `POST /api/v1/predictions/` - Create prediction
- `GET /api/v1/predictions/` - List predictions (with pagination)
- `GET /api/v1/predictions/{prediction_id}` - Get specific prediction
- `GET /api/v1/predictions/video/{video_id}` - Get prediction for video
- `GET /api/v1/predictions/exercise/{exercise_id}` - Get predictions for exercise
- `GET /api/v1/predictions/patient/{patient_id}` - Get patient's predictions
- `PUT /api/v1/predictions/{prediction_id}/feedback` - Add doctor feedback

## Security Features

- Password hashing using SHA-256
- JWT-based authentication
- Role-based access control (Doctor/Patient)
- File upload size limits
- Input validation using Pydantic models

## Development Guidelines

- All IDs are strings (not ObjectId)
- Timestamps are stored in ISO format
- File uploads are stored locally
- AI model integration is handled through custom service
- Pagination is implemented for list endpoints

## Error Handling

- Standard HTTP status codes
- Detailed error messages
- Validation errors for invalid inputs
- File upload error handling
- AI processing error handling

## Testing

- API endpoints can be tested using FastAPI's built-in Swagger UI
- Available at `/docs` when server is running

## Documentation

- API documentation available at `/docs`
- MongoDB schema documentation in `MONGODB_SCHEMA.md`
- Code comments and docstrings for detailed implementation

## Environment Variables

Additional environment variables to configure:

```
JWT_SECRET_KEY=your-secret-key
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760  # 10MB in bytes
```

## Dependencies

Key dependencies from requirements.txt:

- fastapi
- uvicorn
- motor
- pydantic
- python-jose[cryptography]
- passlib[bcrypt]
- python-multipart
- aiofiles

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
