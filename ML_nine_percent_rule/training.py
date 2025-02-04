import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Function to train and evaluate models
def train_and_evaluate(X_train, y_train, X_test, y_test, model_name):
    models = {
        "Logistic Regression": LogisticRegression(),
        "Support Vector Machine": SVC(),
        "Random Forest": RandomForestClassifier()
    }

    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        results[name] = accuracy
        print(f"{model_name} - {name}: {accuracy}")

    # Selecting the best model
    best_model = max(results, key=results.get)
    print(f"{model_name} - Best Model: {best_model}")
    return best_model

# Define file paths for training and testing data
data_paths = {
    "BODY": {
        "X_train": "pose_data_csv/BODY/train/X_train.csv",
        "y_train": "pose_data_csv/BODY/train/y_train.csv",
        "X_test": "pose_data_csv/BODY/test/X_test.csv",
        "y_test": "pose_data_csv/BODY/test/y_test.csv"
    },
    "FACE_NECK": {
        "X_train": "pose_data_csv/FACE_NECK/train/X_train.csv",
        "y_train": "pose_data_csv/FACE_NECK/train/y_train.csv",
        "X_test": "pose_data_csv/FACE_NECK/test/X_test.csv",
        "y_test": "pose_data_csv/FACE_NECK/test/y_test.csv"
    },
    "RIGHT_ARM": {
        "X_train": "pose_data_csv/RIGHT_ARM/train/X_train.csv",
        "y_train": "pose_data_csv/RIGHT_ARM/train/y_train.csv",
        "X_test": "pose_data_csv/RIGHT_ARM/test/X_test.csv",
        "y_test": "pose_data_csv/RIGHT_ARM/test/y_test.csv"
    },
    "LEFT_ARM": {
        "X_train": "pose_data_csv/LEFT_ARM/train/X_train.csv",
        "y_train": "pose_data_csv/LEFT_ARM/train/y_train.csv",
        "X_test": "pose_data_csv/LEFT_ARM/test/X_test.csv",
        "y_test": "pose_data_csv/LEFT_ARM/test/y_test.csv"
    },
    "RIGHT_LEG": {
        "X_train": "pose_data_csv/RIGHT_LEG/train/X_train.csv",
        "y_train": "pose_data_csv/RIGHT_LEG/train/y_train.csv",
        "X_test": "pose_data_csv/RIGHT_LEG/test/X_test.csv",
        "y_test": "pose_data_csv/RIGHT_LEG/test/y_test.csv"
    },
    "LEFT_LEG": {
        "X_train": "pose_data_csv/LEFT_LEG/train/X_train.csv",
        "y_train": "pose_data_csv/LEFT_LEG/train/y_train.csv",
        "X_test": "pose_data_csv/LEFT_LEG/test/X_test.csv",
        "y_test": "pose_data_csv/LEFT_LEG/test/y_test.csv"
    }
}

# Loop through each body part, train models, and evaluate
for body_part, paths in data_paths.items():
    # Load training and testing data
    X_train = pd.read_csv(paths["X_train"]).values
    y_train = pd.read_csv(paths["y_train"]).values
    X_test = pd.read_csv(paths["X_test"]).values
    y_test = pd.read_csv(paths["y_test"]).values

    # Call the function to train and evaluate models
    best_model_name = train_and_evaluate(X_train, y_train, X_test, y_test, body_part)

    # Test the best model using the provided test sets
    if best_model_name == "Logistic Regression":
        best_model = LogisticRegression()
    elif best_model_name == "Support Vector Machine":
        best_model = SVC()
    elif best_model_name == "Random Forest":
        best_model = RandomForestClassifier()

    best_model.fit(X_train, y_train)

    # Predict for each body part and calculate score
    y_pred1 = best_model.predict(X_test)
    y_pred1 = [18 if i == 1 else 0 for i in y_pred1]
    print(f"{body_part} - BODY: {y_pred1}")

    # Load the test data for other body parts
    test_face_neck = pd.read_csv("pose_data_csv/FACE_NECK/test/X_test.csv")
    y_pred2 = best_model.predict(test_face_neck)
    y_pred2 = [9 if i == 1 else 0 for i in y_pred2]
    print(f"FACE_NECK: {y_pred2}")

    test_right_arm = pd.read_csv("pose_data_csv/RIGHT_ARM/test/X_test.csv")
    y_pred3 = best_model.predict(test_right_arm)
    y_pred3 = [18 if i == 1 else 0 for i in y_pred3]
    print(f"RIGHT_ARM: {y_pred3}")

    test_left_arm = pd.read_csv("pose_data_csv/LEFT_ARM/test/X_test.csv")
    y_pred4 = best_model.predict(test_left_arm)
    y_pred4 = [18 if i == 1 else 0 for i in y_pred4]
    print(f"LEFT_ARM: {y_pred4}")

    test_right_leg = pd.read_csv("pose_data_csv/RIGHT_LEG/test/X_test.csv")
    y_pred5 = best_model.predict(test_right_leg)
    y_pred5 = [18 if i == 1 else 0 for i in y_pred5]
    print(f"RIGHT_LEG: {y_pred5}")

    test_left_leg = pd.read_csv("pose_data_csv/LEFT_LEG/test/X_test.csv")
    y_pred6 = best_model.predict(test_left_leg)
    y_pred6 = [18 if i == 1 else 0 for i in y_pred6]
    print(f"LEFT_LEG: {y_pred6}")

    # Calculate the total score
    total_score = [sum(i) for i in zip(y_pred1, y_pred2, y_pred3, y_pred4, y_pred5, y_pred6)]
    print(f"Total score: {total_score}")
