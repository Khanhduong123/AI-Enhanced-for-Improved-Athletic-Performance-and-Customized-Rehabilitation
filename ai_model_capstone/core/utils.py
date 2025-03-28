import os
import json
import mlflow
from typing import Any
import numpy as np

def create_experiment(name: str, artifact_location: str, tags: dict[str, Any]):
    
    try:
        exp_id = mlflow.create_experiment(
            name=name,
            artifact_location=artifact_location,
            tags=tags
        )
    
    except Exception as e:
        print(f"Experiment {name} already exists")
        exp_id = mlflow.get_experiment_by_name(name).experiment_id

    return exp_id