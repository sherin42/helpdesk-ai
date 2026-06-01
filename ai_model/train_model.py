import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.naive_bayes import MultinomialNB

from sklearn.pipeline import Pipeline

import joblib


# LOAD DATASET
data = pd.read_csv("dataset.csv")


# INPUT
X = data["text"]


# OUTPUT
y = data["department"]


# CREATE PIPELINE
model = Pipeline([

    ("tfidf", TfidfVectorizer()),

    ("classifier", MultinomialNB())

])


# TRAIN MODEL
model.fit(X, y)


# SAVE MODEL
joblib.dump(model, "department_model.pkl")


print("AI Model Trained Successfully!")