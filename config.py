import yaml

class Config:
    def __init__(self, yaml_path="config/hyperparams.yaml"):
        with open(yaml_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

    def get(self, key, default=None):
        keys = key.split(".")
        value = self.config
        for k in keys:
            value = value.get(k, {})
        return value if value else default


if __name__ == "__main__":
    # pass
    config=  Config("config/hyperparams.yaml")
    print(type(config.get("data.json_path_train")))