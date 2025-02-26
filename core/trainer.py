import sys
import time
import torch
from datetime import timedelta
import sklearn.metrics as metrics
import mlflow


class Trainer:
    def __init__(self, model, optimizer, criterion, scheduler= None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = model.to(self.device)
        self.optimizer = optimizer
        self.criteria = criterion
        self.scheduler = scheduler
        self.best_acc = 0
        self.all_preds = []
        self.all_labels = []
        self.cache = {
            "train_loss": [],
            "train_acc": [],
            "val_loss": [],
            "val_acc": [],
            "lr": []
        }
    

    # def get_edge_index(self):
    #     """
    #     Trả về ma trận kề (edge_index) cho 33 keypoints của Mediapipe.
    #     """
    #     edges = [
    #         (0, 1), (1, 2), (2, 3), (3, 7),  # Tay trái
    #         (0, 4), (4, 5), (5, 6), (6, 8),  # Tay phải
    #         (9, 10), (11, 12),  # Hông
    #         (11, 13), (13, 15), (15, 17), (15, 19), (15, 21),  # Chân trái
    #         (12, 14), (14, 16), (16, 18), (16, 20), (16, 22),  # Chân phải
    #         (11, 23), (12, 24), (23, 24),  # Kết nối hông
    #         (23, 25), (25, 27), (27, 29), (29, 31),  # Chân trái
    #         (24, 26), (26, 28), (28, 30), (30, 32)   # Chân phải
    #     ]
    #     edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()  # (2, num_edges)
    #     return edge_index

    def save_checkpoint(self, path):
        if not self.cache["val_acc"]:
            return
        
        acc = self.cache["val_acc"][-1]["accuracy"]
        if acc >= self.best_acc:
            self.best_acc = acc
            params = {
                'model': self.model.state_dict(),
                'optimizer': self.optimizer.state_dict(),
                'scheduler': self.scheduler.state_dict() if self.scheduler is not None else None,
                'cache': self.cache
            }
            torch.save(params, path)
        print("[+] Save checkpoint successfully!")
    

    def load_checkpoint(self, path):
        checkpoint = torch.load(path)
        self.model.load_state_dict(checkpoint['model'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])
        self.scheduler.load_state_dict(checkpoint['scheduler'])
        self.cache = checkpoint['cache']
        print("[+] Load checkpoint successfully!")
    

    def compute_metrics(self, preds, labels):
        preds = preds.cpu().numpy() if isinstance(preds, torch.Tensor) else preds
        labels = labels.cpu().numpy() if isinstance(labels, torch.Tensor) else labels

        accuracy = sum([1 for i, j in zip(preds, labels) if i == j]) / len(labels)
        precision = metrics.precision_score(labels, preds, average='micro')
        recall = metrics.recall_score(labels, preds, average='micro')
        f1 = metrics.f1_score(labels, preds, average='micro')

        return {
            'accuracy' : round(accuracy, 7),
            'precision' : round(precision, 7),
            'recall' : round(recall, 7),
            'f1' : round(f1, 7)
        }
    
    def forward(self, dataloader, fw_model='train'):

        if not isinstance(dataloader, torch.utils.data.DataLoader):
            raise TypeError(f"Expected `dataloader` to be a DataLoader, but got {type(dataloader)}")

        if fw_model == 'train':
            self.model.train()
        else:
            self.model.eval()

        cache = {'loss': [], 'acc': []}
        N = len(dataloader)
        for i , data in enumerate(dataloader, 1):
            if fw_model == 'train':
                self.optimizer.zero_grad()
            
            inputs, labels = data
            inputs, labels = inputs.to(self.device), labels.to(self.device)

            with torch.set_grad_enabled(fw_model == 'train'):
                #TODO: if spoter model ==> self.model(inputs).squeeze(1)  else: outputs = model(X_batch, edge_index, batch)
                outputs = self.model(inputs).squeeze(1) 
                loss = self.criteria(outputs, labels)
                preds = outputs.argmax(dim=1)
                self.all_preds.extend(preds.cpu().tolist())
                self.all_labels.extend(labels.cpu().tolist())

                if fw_model == 'train':
                    loss.backward()
                    self.optimizer.step()
            
            cache['loss'].append(loss.item())
            acc = self.compute_metrics(preds, labels)
            cache['acc'].append(acc)
            print("\r",end="")
            print(f"{fw_model.capitalize()} step: {i} / {N} - Acc: {acc['accuracy']}", end="" if i != N else "\n")
        
        loss = sum(cache['loss']) / len(cache['loss'])
        acc = [[i["accuracy"] for i in cache["acc"]], [i["precision"] for i in cache["acc"]], [i["recall"] for i in cache["acc"]], [i["f1"] for i in cache["acc"]]]
        acc = {
            "accuracy": round(sum(acc[0]) / len(acc[0]), 7),
            "precision": round(sum(acc[1]) / len(acc[1]), 7),
            "recall": round(sum(acc[2]) / len(acc[2]), 7),
            "f1": round(sum(acc[3]) / len(acc[3]), 7)
        }

        self.cache[f"{fw_model}_loss"].append(loss)
        self.cache[f"{fw_model}_acc"].append(acc)
    

    def fit(self, trainloader, valid_loader= None, epochs=2 , checkpoint='checkpoint.pt'):
        print(f"Running on: {torch.cuda.get_device_name(torch.cuda.current_device())}")
        print(f"Total update step: {len(trainloader) * epochs}")

        for epoch in range(1, epochs + 1):
            start_time = time.time()
            print(f"Epoch: {epoch}")
            logs = []
            current_lr = f"{self.optimizer.param_groups[0]['lr']:e}"

            try:
                self.forward(trainloader, 'train')
                train_loss = round(self.cache['train_loss'][-1], 5)
                train_acc = self.cache['train_acc'][-1]

                mlflow.log_metric('train_loss', train_loss, step=epoch)
                for metric_name, metric_value in train_acc.items():
                    mlflow.log_metric(f'train_{metric_name}', metric_value, step=epoch)


                train_acc = [str(k) + ": " + str(v) for k, v in self.cache['train_acc'][-1].items()]
                train_acc = " - ".join(train_acc)
                logs.append(f"\t=> Train epoch: loss: {train_loss} - {train_acc}")

            except KeyboardInterrupt:
                sys.exit()

            if valid_loader is not None:
                try:
                    self.forward(valid_loader, 'valid') 
                    valid_loss = round(self.cache['valid_loss'][-1], 5)
                    valid_acc = self.cache['valid_acc'][-1]

                    mlflow.log_metric('valid_loss', valid_loss, step=epoch)
                    for metric_name, metric_value in valid_acc.items():
                        mlflow.log_metric(f'valid_{metric_name}', metric_value, step=epoch)

                    valid_acc = [str(k) + ": " + str(v) for k, v in self.cache['valid_acc'][-1].items()]
                    valid_acc = " - ".join(valid_acc)
                    logs.append(f"\t=> Valid epoch: loss: {valid_loss} - {valid_acc}")

                except KeyboardInterrupt:
                    sys.exit()

            total_time = round(time.time() - start_time)
            logs.append(f"\t=> Learning Rate: {current_lr} - Time: {timedelta(seconds=int(total_time))}/step\n")
            print("\n".join(logs))
            self.cache["lr"].append(current_lr)
            self.save_checkpoint(checkpoint)      