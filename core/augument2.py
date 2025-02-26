import numpy as np
from core.utils import load_json, save_json, json_to_numpy, numpy_to_json

class Augmentation:
    def __init__(self, json_data):
        self.json_data = json_data
        self.skeleton = json_to_numpy(json_data)

    def jittering(self, noise_level=0.01):
        noise = np.random.normal(loc=0, scale=noise_level, size=self.skeleton.shape)
        self.skeleton += noise
        return numpy_to_json(self.skeleton, self.json_data)

    def scaling(self, scale_range=(0.9, 1.1)):
        scale_factor = np.random.uniform(scale_range[0], scale_range[1])
        self.skeleton *= scale_factor
        return numpy_to_json(self.skeleton, self.json_data)

    def rotation(self, angle_range=(-15, 15)):
        angle = np.radians(np.random.uniform(angle_range[0], angle_range[1]))
        cos_val, sin_val = np.cos(angle), np.sin(angle)
        rotation_matrix = np.array([[cos_val, -sin_val], [sin_val, cos_val]])
        self.skeleton[:, :, :2] = np.dot(self.skeleton[:, :, :2] - np.mean(self.skeleton[:, :, :2], axis=0), rotation_matrix) + np.mean(self.skeleton[:, :, :2], axis=0)
        return numpy_to_json(self.skeleton, self.json_data)

if __name__ == "__main__":
    input_json_path = ""
    output_json_path = ""

    json_data = load_json(input_json_path)
    aug = Augmentation(json_data)
    augmented_data = aug.jittering()
    save_json(augmented_data, output_json_path)
