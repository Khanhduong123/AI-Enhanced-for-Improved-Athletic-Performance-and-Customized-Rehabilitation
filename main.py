
from core.dataloader import YogaDataset
from torch.utils.data import DataLoader

def main():
    #load data
    json_folder = "data/keypoints/public_data"
    dataset = YogaDataset(json_folder, max_frames=100)  # Định nghĩa số frame cố định

    batch_size = 4
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Kiểm tra 1 batch dữ liệu
    for batch in dataloader:
        X_batch, y_batch = batch
        print("X_batch shape:", X_batch.shape)  # (batch_size, max_frames, 33, 3)
        print("y_batch shape:", y_batch.shape)  # (batch_size,)
        print("y_batch values:", y_batch)  # Nhãn của từng sample
        break

if __name__ == "__main__":
    main()