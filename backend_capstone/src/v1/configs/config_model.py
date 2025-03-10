import os

class Config:
    # Current file's directory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Construct the checkpoint path:
    CHECKPOINT_PATH_GCN = os.path.join(
        BASE_DIR, 
        "checkpoints", 
        "gcn", 
        "pretrain", 
        "best_checkpoint.pt"
    )

    CHECKPOINT_PATH_SPOTER = os.path.join(
        BASE_DIR, 
        "checkpoints", 
        "spoter", 
        "pretrain", 
        "best_checkpoint.pt"
    )

    MODEL_NAME = "gcn" # or "gcn"

    # For example, if you have 4 classes:
    CLASS_LABELS = ["Garland_Pose", "Happy_Baby_Pose", "Head_To_Knee_Pose", "Lunge_Pose", "Mountain_Pose","Plank_Pose","Raised_Arms_Pose","Seated_Forward_Bend","Staff_Pose","Standing_Forward_Bend"]
