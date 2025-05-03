
# Exercise Tracker Application

## Project Description
This project develops an application that utilizes AI to help patients perform physical therapy exercises correctly at home. The system uses AI models to recognize movements from videos, evaluate accuracy, and provide feedback to support training and recovery.


This is a full-stack exercise tracking system that includes:

- A **FastAPI-based backend** for user, exercise, and video management with AI-based motion analysis
- A **React Native frontend** using **Expo** for doctors and patients to interact with the system

---

## 🧠 Backend – FastAPI Server

### Features

- User Management (Doctors and Patients)
- Exercise Assignment
- Video Upload and Processing
- AI-powered Motion Analysis
- Progress Tracking

### Tech Stack

- FastAPI: High-performance web framework
- MongoDB: NoSQL database for flexible schema
- Motor: Async MongoDB driver
- Pydantic: Data validation
- Python 3.10

### Setup Instructions

#### Prerequisites

- Python 3.10
- MongoDB

#### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
MONGO_URI=mongodb://localhost:27017
DB_NAME=exercise_tracker_db
```

#### Installation

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



### API Documentation

Once the server is running, you can access the interactive API documentation at:

- Swagger UI: `http://localhost:7860/docs`
- ReDoc: `http://localhost:7860/redoc`


### Database Schema

#### Users Collection

- `_id`: ObjectId (Unique identifier)  
- `email`: String (Unique email address)  
- `full_name`: String  
- `role`: String ("Doctor" or "Patient")  
- `hashed_password`: String  
- `created_at`: DateTime  
- `updated_at`: DateTime  

#### Exercises Collection

- `_id`: ObjectId  
- `name`: String  
- `description`: String  
- `assigned_by`: ObjectId  
- `assigned_to`: ObjectId  
- `assigned_date`: DateTime  
- `due_date`: DateTime (Optional)  
- `status`: String ("Pending", "Completed", "Not Completed")  
- `created_at`: DateTime  
- `updated_at`: DateTime  

#### Videos Collection

- `_id`: ObjectId  
- `patient_id`: ObjectId  
- `exercise_id`: ObjectId  
- `file_path`: String  
- `file_name`: String  
- `file_size`: Number (bytes)  
- `content_type`: String  
- `upload_date`: DateTime  
- `status`: String ("Uploaded", "Processed", "Failed")  
- `created_at`: DateTime  
- `updated_at`: DateTime  

#### Predictions Collection

- `_id`: ObjectId  
- `video_id`: ObjectId  
- `exercise_id`: ObjectId  
- `patient_id`: ObjectId  
- `predicted_motion`: String  
- `confidence_score`: Number (0-1)  
- `model_name`: String  
- `is_match`: Boolean  
- `raw_results`: Object  
- `created_at`: DateTime  

### API Endpoints

#### User Management

- `POST /api/v1/users/`: Register a new user  
- `POST /api/v1/users/login`: Login  
- `GET /api/v1/users/{user_id}`: Get user profile  
- `PUT /api/v1/users/{user_id}`: Update user profile  

#### Exercise Management

- `POST /api/v1/exercises/`: Create a new exercise  
- `GET /api/v1/exercises/{exercise_id}`: Get exercise details  
- `PUT /api/v1/exercises/{exercise_id}`: Update exercise  
- `GET /api/v1/exercises/patient/{patient_id}`: Get patient's exercises  
- `GET /api/v1/exercises/doctor/{doctor_id}`: Get doctor's assigned exercises  

#### Video Management

- `POST /api/v1/predict/`: Upload and analyze a video  
- `GET /api/v1/videos/{video_id}`: Get video with prediction  
- `GET /api/v1/videos/patient/{patient_id}`: Get patient's videos  
- `GET /api/v1/predict/exercise/{exercise_id}/videos`: Get videos for an exercise  

---

## 📱 Frontend – React Native with Expo

### Get started

1. Install dependencies

```bash
npm install
```

2. Start the app

```bash
npx expo start
```

In the output, you'll find options to open the app in a:

- [Development build](https://docs.expo.dev/develop/development-builds/introduction/)
- [Android emulator](https://docs.expo.dev/workflow/android-studio-emulator/)
- [iOS simulator](https://docs.expo.dev/workflow/ios-simulator/)
- [Expo Go](https://expo.dev/go) — a limited sandbox for trying out app development with Expo

### Reset Project

To reset and start fresh:

```bash
npm run reset-project
```

This command will move the starter code to the **app-example** directory and create a blank **app** directory.

## Contact
For any inquiries, please free contact us at: khanhbaoduong789@gmail.com

## License
MIT