import torch
from typing import Dict
# Adjust import as needed based on your folder structure:
from ..configs.config_model import Config
from .model_service import load_model
from ..ai.core_model import SPOTER, YogaGCN 

class ModelProvider:
    """
    A provider class to hold references to loaded models.
    """
    _models: Dict[str, torch.nn.Module] = {}
    _model_name: str = Config.MODEL_NAME
    _classes = Config.CLASS_LABELS

    @classmethod
    def get_model(cls) -> torch.nn.Module:
        """
        Return a loaded model instance, caching it so we only load once.
        """
        if cls._model_name not in cls._models:
            # If your model name is "gcn", build a GCN instance:
            if cls._model_name == "gcn":
                model = YogaGCN(in_channels=3, hidden_dim=256, num_classes=len(cls._classes))
                checkpoint_path = Config.CHECKPOINT_PATH_GCN

            # If you also have "spoter", you could do:
            elif cls._model_name == "spoter":
                model = SPOTER(hidden_dim=18, num_classes=len(cls._classes), max_frame=100, num_heads=9, encoder_layers=1, decoder_layers=1)
                checkpoint_path = Config.CHECKPOINT_PATH_SPOTER

            else:
                raise ValueError(f"Unknown model name: {cls._model_name}")

            # Load the checkpoint from config
            model = load_model(checkpoint_path, model)
            cls._models[cls._model_name] = model

        return cls._models[cls._model_name]

    @classmethod
    def get_model_name(cls) -> str:
        return cls._model_name

    @classmethod
    def get_classes(cls):
        return cls._classes
