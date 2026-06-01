import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.naive_bayes import MultinomialNB

from sklearn.pipeline import Pipeline

import joblib


# LOAD DATASET
data = pd.read_csv("priority_dataset.csv")

# INPUT
X = data["text"]

# OUTPUT
y = data["priority"]

# CREATE PIPELINE
model = Pipeline([
    ('vectorizer', TfidfVectorizer()),
    ('classifier', MultinomialNB())
])

# TRAIN MODEL
model.fit(X, y)

# SAVE MODEL
joblib.dump(model, "priority_model.pkl")

print("Priority AI Model Trained Successfully!")