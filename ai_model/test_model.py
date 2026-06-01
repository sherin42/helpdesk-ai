import joblib

model = joblib.load("department_model.pkl")

while True:

    text = input("Enter ticket: ")

    prediction = model.predict([text])

    print("Predicted Department:", prediction[0])