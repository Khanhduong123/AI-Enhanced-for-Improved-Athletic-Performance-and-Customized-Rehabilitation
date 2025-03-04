import os
import numpy as np
import matplotlib.pyplot as plt
from core.utils import load_json, json_to_numpy
from sklearn.metrics import ConfusionMatrixDisplay
class Visualizer:
    def __init__(self, original_json_path, augmented_json_path):
        """Class Visualizer để hiển thị sự khác biệt giữa dữ liệu gốc và Augmented."""
        self.original_json_path = original_json_path
        self.augmented_json_path = augmented_json_path
        self.original_data = load_json(self.original_json_path)
        self.augmented_data = load_json(self.augmented_json_path)

    def visualize(self):
        """Vẽ biểu đồ so sánh tọa độ keypoints trước và sau augmentation."""
        original_np = json_to_numpy(self.original_data)
        augmented_np = json_to_numpy(self.augmented_data)

        original_x, original_y = original_np[0][:, 0], original_np[0][:, 1]
        augmented_x, augmented_y = augmented_np[0][:, 0], augmented_np[0][:, 1]

        diff_x = np.abs(original_x - augmented_x)
        diff_y = np.abs(original_y - augmented_y)
        diff_distance = np.sqrt(diff_x ** 2 + diff_y ** 2)

        plt.figure(figsize=(6, 6))
        plt.scatter(original_x, original_y, c='blue', label='Original', alpha=0.7)
        plt.scatter(augmented_x, augmented_y, c='red', label='Augmented', alpha=0.7, marker='x')

        for i in range(len(original_x)):
            plt.plot([original_x[i], augmented_x[i]], [original_y[i], augmented_y[i]], 'gray', linestyle="--", alpha=0.5)
            plt.text((original_x[i] + augmented_x[i]) / 2, (original_y[i] + augmented_y[i]) / 2,
                     f"{diff_distance[i]:.4f}", fontsize=8, color='black')

        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.title(f"So sánh keypoints: {os.path.basename(self.original_json_path)}")
        plt.legend()
        plt.gca().invert_yaxis()
        plt.show()

def plot_confusion_matrix(cm, trainset,save_path):
    cm_display = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=trainset.classes)
    plt.figure(figsize=(12, 15))
    cm_display.plot(cmap=plt.cm.Blues, values_format='d')
    plt.xticks(rotation=45, ha='right')
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    print(f"[+] Confusion matrix saved to {save_path}")
    

if __name__ == "__main__":
    original_json_path = ""
    augmented_json_path = ""

    visualizer = Visualizer(original_json_path, augmented_json_path)
    visualizer.visualize()
