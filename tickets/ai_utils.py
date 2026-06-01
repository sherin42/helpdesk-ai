import joblib

# LOAD MODEL
model = joblib.load(
    'ai_model/department_model.pkl'
)

# PREDICT FUNCTION
def predict_department(text):

    prediction = model.predict([text])[0]

    confidence = max(
        model.predict_proba([text])[0]
    )

    return prediction, confidence