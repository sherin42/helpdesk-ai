import os
import joblib

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

model_path = os.path.join(
    BASE_DIR,
    'ai_model',
    'priority_model.pkl'
)

model = joblib.load(model_path)


def predict_priority(text):

    prediction = model.predict([text])

    return prediction[0]