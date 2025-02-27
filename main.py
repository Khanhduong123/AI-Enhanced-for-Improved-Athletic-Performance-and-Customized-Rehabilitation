import mlflow
import torch
from core.dataset import YogaDataset
from torch.utils.data import DataLoader
import torch.nn as nn
from core.utils import create_experiment
import torch.optim as optim
from core.model import SPOTER
from core.trainer import Trainer
from mlflow.models import infer_signature
from torchinfo import summary
import sys
def main():
    #load data
    batch_size = 4
    num_epochs = 10
    learning_rate = 0.001

    json_folder = "data/keypoints/public_data"
    
    dataset = YogaDataset(json_folder, max_frames=100)  # Định nghĩa số frame cố định
    trainloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)


    exp_id = create_experiment(
        name="pytorch_test",
        artifact_location="pytorch_test_artifact",
        tags={"env": "dev", "version": "1.0.0"}
    )

    model = SPOTER(num_classes=4, hidden_dim=72)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    trainer = Trainer(model,optimizer,criterion,None)


    with mlflow.start_run(run_name="Pytorch_test", experiment_id=exp_id,log_system_metrics=True) as run:
        params = {
            "epochs": num_epochs,
            "learning_rate": learning_rate,
            "batch_size": batch_size,
            "loss_function": criterion.__class__.__name__,
            "optimizer": optimizer.__class__.__name__,
        }

        sample_inputs, _ = next(iter(trainloader))
        X = sample_inputs.to(device = "cuda" if torch.cuda.is_available() else "cpu")
        signature = infer_signature(X.cpu().numpy(), model(X).detach().cpu().numpy())
        mlflow.log_params(params)
        with open("summary/model_summary.txt", "w", encoding="utf-8") as f:
            f.write(str(summary(model)))
        mlflow.log_artifact("summary/model_summary.txt")

        try:
            trainer.fit(trainloader,None ,num_epochs)
            mlflow.pytorch.log_model(model, "models", signature=signature)
        except KeyboardInterrupt:
            sys.exit()


    

if __name__ == "__main__":
    main()