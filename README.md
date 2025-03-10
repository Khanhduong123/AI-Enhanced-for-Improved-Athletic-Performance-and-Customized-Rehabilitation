# AI-Enhanced-for-Improved-Athletic-Performance-and-Customized-Rehabilitation

## Project Description
This project develops an application that utilizes AI to help patients perform physical therapy exercises correctly at home. The system uses AI models to recognize movements from videos, evaluate accuracy, and provide feedback to support training and recovery.

## Folder Structure

### 1. **ai_model_capstone**
This folder contains AI model-related components:
- **checkpoints/**: Stores trained model weights.
  - `gcn/finetune`: Fine-tuned weights for the GCN model.
  - `gcn/pretrain`: Pretrained weights for the GCN model.
  - `spoter/finetune`: Fine-tuned weights for the Spoter model.
  - `spoter/pretrain`: Pretrained weights for the Spoter model.
- **config/**: Configuration settings for the AI model.
- **core/**: Core components of the AI system.
- **data/**: Training and evaluation data for AI models.
  - `keypoints/`: Stores skeleton keypoint data.
  - `processed_video/`: Processed videos.
  - `raw_video/`: Raw unprocessed videos.
- **images/**: Contains images related to the project.
- **notebook/**: Jupyter notebooks supporting research and model training.
- **summary/**: Summary of model training results.

### 2. **backend_capstone**
Contains the backend API for data processing and interaction with the AI model.
- **src/v1/**: Main backend code.
  - `configs/`: API configurations and checkpoint management.
  - `models/`: Defines AI models used in the backend.
  - `providers/`: Provides supporting components for the API.
  - `routers/`: Defines API endpoints.
  - `services/`: Handles backend business logic.
- **temp_videos/**: Temporarily stores videos before processing.

### 3. **frontend_capstone**
User interface for patients to perform therapy exercises and receive AI-generated feedback.

## Installation
### System Requirements
- Python 3.10+
- Node.js 16+
- FastAPI
- React.js
- Mediapipe 

### Backend Installation
```sh
cd backend_capstone
pip install -r requirements.txt
uvicorn src.v1.main:app --reload
```

### Frontend Installation
```sh
cd frontend_capstone
npm install
npm start
```

## Usage Guide
1. Start the backend and frontend.
2. Upload an exercise video to the system.
3. AI analyzes and evaluates the movement.
4. Users receive feedback on accuracy and necessary corrections.

## Contact
For any inquiries, please free contact us at: khanhdbse172248@fpt.edu.vn