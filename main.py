import mlflow
import torch
from core.dataset import YogaDataset
from torch.utils.data import DataLoader
import torch.nn as nn
from core.utils import create_experiment
import torch.optim as optim
from core.model import get_model
from core.trainer import Trainer
from mlflow.models import infer_signature
from torchinfo import summary
from config import Config
import sys


 #load data
# batch_size = 4
# num_epochs = 10
# learning_rate = 0.001
# model_name = "gcn"
# is_pretrain = False
def main(): 
    config = Config()
    checkpoint_dir =  f"checkpoints/{str(config.get('model.model_name'))}/{'pretrain' if bool(config.get('model.pretrained')) else 'finetune'}"
    
    trainset = YogaDataset(config.get('data.json_path_train'), max_frames=config.get('data.max_frame'))  # Định nghĩa số frame cố định
    trainloader = DataLoader(trainset, batch_size=config.get('data.batch_size'), shuffle=True)

    valset = YogaDataset(config.get('data.json_path_val'), max_frames=config.get('data.max_frame'))  # Định nghĩa số frame cố định
    validloader = DataLoader(valset, batch_size=config.get('data.batch_size'), shuffle=False)


    exp_id = create_experiment(
        name=config.get("mlflow.name_id"),
        artifact_location=config.get("mlflow.artifact_location"), 
        tags={"env": "dev", "version": "1.0.0"}
    )

    model = get_model(config)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=config.get("train.lr"))
    trainer = Trainer(model,optimizer,criterion,None,config.get('model.model_name'),bool(config.get('model.pretrained')))


    with mlflow.start_run(run_name="Pytorch_test", experiment_id=exp_id,log_system_metrics=True) as run:
        params = {
            "epochs": config.get("train.num_epochs"),
            "learning_rate": config.get("train.lr"),
            "batch_size": config.get("data.batch_size"),
            "loss_function": criterion.__class__.__name__,
            "optimizer": optimizer.__class__.__name__,
        }
        if config.get('model.model_name') == "spoter":

            sample_inputs, _ = next(iter(trainloader))
            X = sample_inputs.to(device = "cuda" if torch.cuda.is_available() else "cpu")
        
        elif config.get('model.model_name') == "gcn":
            sample_inputs, _ = next(iter(trainloader))
            X = sample_inputs.to(device = "cuda" if torch.cuda.is_available() else "cpu")
            batch_size, num_frames, num_keypoints, keypoint_dim = X.shape
            X = X.view(batch_size * num_frames * num_keypoints, keypoint_dim)

            edge_index = trainer.get_edge_index().to(X.device)
            batch = torch.arange(batch_size, device=X.device).repeat_interleave(num_frames * num_keypoints)
            output = model(X, edge_index, batch).detach()
            signature = infer_signature(X.cpu().numpy(), output.cpu().numpy())

            
        
        mlflow.log_params(params)
        with open("summary/model_summary.txt", "w", encoding="utf-8") as f:
            f.write(str(summary(model)))
        mlflow.log_artifact("summary/model_summary.txt")

        try:
            trainer.fit(trainloader,validloader,config.get("train.num_epochs"),checkpoint_dir)
            mlflow.pytorch.log_model(model, "models", signature=signature)
        except KeyboardInterrupt:
            sys.exit()


    

if __name__ == "__main__":
    main()