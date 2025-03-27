import os

class Config:
    # Current file's directory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Construct the checkpoint path:
    CHECKPOINT_PATH_GCN = os.path.join(
        BASE_DIR, 
        "checkpoints", 
        "gcn", 
        "finetune", 
        "best_checkpoint.pt"
    )

    CHECKPOINT_PATH_SPOTER = os.path.join(
        BASE_DIR, 
        "checkpoints", 
        "spoter", 
        "finetune", 
        "best_checkpoint.pt"
    )

    MODEL_NAME = "gcn" # or "gcn"

    # For example, if you have 4 classes:
    CLASS_LABELS = ["Dangchanraxanghiengminh", "Ngoithangbangtrengot", "Sodatvuonlen", "Xemxaxemgan"]
