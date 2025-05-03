from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Query, Depends
from datetime import datetime
from ..models.prediction import Prediction
from ..services.prediction_service import get_prediction, get_exercise_predictions, get_patient_predictions
from ..services.user_service import get_user
from ..services.exercise_service import get_doctor_assigned_exercises, get_exercise
from ..core.pagination import PaginationParams, get_pagination_params

router = APIRouter(prefix="/predictions", tags=["Predictions"])

@router.get("/{prediction_id}", response_model=Prediction)
async def get_prediction_by_id(prediction_id: str):
    """
    Get a prediction by ID
    
    Args:
        prediction_id: The unique identifier of the prediction
        
    Returns:
        Prediction object with all details
        
    Raises:
        HTTPException: If prediction not found
    """
    try:
        prediction = await get_prediction(prediction_id)
        if not prediction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prediction with ID {prediction_id} not found"
            )
        return prediction
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving prediction: {str(e)}"
        )

@router.get("/patient/{patient_id}", response_model=List[Prediction])
async def get_predictions_for_patient(
    patient_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[str] = None,
    pagination: PaginationParams = Depends(get_pagination_params)
):
    """
    Get all predictions for a specific patient with filtering and pagination
    
    Args:
        patient_id: The patient's unique identifier
        start_date: Optional filter for predictions after this date
        end_date: Optional filter for predictions before this date
        status: Optional filter for prediction status
        pagination: Pagination parameters
        
    Returns:
        List of predictions matching the criteria
        
    Raises:
        HTTPException: If patient not found or other errors occur
    """
    try:
        # Verify patient exists
        await get_user(patient_id)
        
        # Get filtered predictions for this patient
        return await get_patient_predictions(
            patient_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
            skip=pagination.skip,
            limit=pagination.limit
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving patient predictions: {str(e)}"
        )

@router.get("/exercise/{exercise_id}", response_model=List[Prediction])
async def get_predictions_for_exercise(
    exercise_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    confidence_threshold: Optional[float] = None,
    pagination: PaginationParams = Depends(get_pagination_params)
):
    """
    Get all predictions for a specific exercise with filtering and pagination
    
    Args:
        exercise_id: The exercise's unique identifier
        start_date: Optional filter for predictions after this date
        end_date: Optional filter for predictions before this date
        confidence_threshold: Optional minimum confidence score
        pagination: Pagination parameters
        
    Returns:
        List of predictions matching the criteria
        
    Raises:
        HTTPException: If exercise not found or other errors occur
    """
    try:
        # Verify exercise exists
        await get_exercise(exercise_id)
        
        return await get_exercise_predictions(
            exercise_id,
            start_date=start_date,
            end_date=end_date,
            confidence_threshold=confidence_threshold,
            skip=pagination.skip,
            limit=pagination.limit
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving exercise predictions: {str(e)}"
        )

@router.get("/doctor/{doctor_id}", response_model=List[Dict[str, Any]])
async def get_predictions_for_doctor_patients(
    doctor_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[str] = None,
    pagination: PaginationParams = Depends(get_pagination_params)
):
    """
    Get all predictions for patients assigned by a specific doctor with filtering and pagination
    
    Args:
        doctor_id: The doctor's unique identifier
        start_date: Optional filter for predictions after this date
        end_date: Optional filter for predictions before this date
        status: Optional filter for prediction status
        pagination: Pagination parameters
        
    Returns:
        List of predictions with exercise details
        
    Raises:
        HTTPException: If doctor not found or other errors occur
    """
    try:
        # Verify doctor exists and is a doctor
        doctor = await get_user(doctor_id)
        if doctor.role != "Doctor":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a doctor"
            )
        
        # Get all exercises assigned by this doctor
        doctor_exercises = await get_doctor_assigned_exercises(doctor_id)
        
        result = []
        for exercise in doctor_exercises:
            # Get filtered predictions for each exercise
            predictions = await get_exercise_predictions(
                str(exercise.id),
                start_date=start_date,
                end_date=end_date,
                status=status,
                skip=pagination.skip,
                limit=pagination.limit
            )
            
            for prediction in predictions:
                result.append({
                    "exercise": {
                        "id": str(exercise.id),
                        "name": exercise.name,
                        "description": exercise.description,
                        "status": exercise.status
                    },
                    "prediction": {
                        "id": str(prediction.id),
                        "predicted_motion": prediction.predicted_motion,
                        "confidence_score": prediction.confidence_score,
                        "is_match": prediction.is_match,
                        "created_at": prediction.created_at
                    },
                    "patient_id": str(prediction.patient_id)
                })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving doctor predictions: {str(e)}"
        )

@router.get("/doctor/{doctor_id}/patient/{patient_id}", response_model=List[Dict[str, Any]])
async def get_predictions_by_doctor_and_patient(
    doctor_id: str,
    patient_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[str] = None,
    pagination: PaginationParams = Depends(get_pagination_params)
):
    """
    Get all predictions for a specific patient assigned by a specific doctor with filtering and pagination
    
    Args:
        doctor_id: The doctor's unique identifier
        patient_id: The patient's unique identifier
        start_date: Optional filter for predictions after this date
        end_date: Optional filter for predictions before this date
        status: Optional filter for prediction status
        pagination: Pagination parameters
        
    Returns:
        List of predictions with exercise details
        
    Raises:
        HTTPException: If doctor/patient not found or other errors occur
    """
    try:
        # Verify doctor exists and is a doctor
        doctor = await get_user(doctor_id)
        if doctor.role != "Doctor":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a doctor"
            )
        
        # Verify patient exists
        await get_user(patient_id)
        
        # Get all exercises assigned by this doctor to this patient
        doctor_exercises = await get_doctor_assigned_exercises(doctor_id)
        patient_exercises = [e for e in doctor_exercises if str(e.assigned_to) == patient_id]
        
        result = []
        for exercise in patient_exercises:
            # Get filtered predictions for each exercise
            predictions = await get_exercise_predictions(
                str(exercise.id),
                start_date=start_date,
                end_date=end_date,
                status=status,
                skip=pagination.skip,
                limit=pagination.limit
            )
            
            for prediction in predictions:
                # Double check this prediction belongs to the patient
                if str(prediction.patient_id) == patient_id:
                    result.append({
                        "exercise": {
                            "id": str(exercise.id),
                            "name": exercise.name,
                            "description": exercise.description,
                            "status": exercise.status,
                            "assigned_date": exercise.assigned_date
                        },
                        "prediction": {
                            "id": str(prediction.id),
                            "predicted_motion": prediction.predicted_motion,
                            "confidence_score": prediction.confidence_score,
                            "is_match": prediction.is_match,
                            "created_at": prediction.created_at
                        }
                    })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving doctor-patient predictions: {str(e)}"
        ) 