import joblib
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "sentiment_model.joblib")
model = joblib.load(MODEL_PATH)


def analyze_satisfaction(message):
    if not message or len(message.strip()) == 0:
        return 0
    prediction = model.predict([message])
    return int(prediction[0])


''' Training of the model

Dataset :
https://www.kaggle.com/datasets/jp797498e/twitter-entity-sentiment-analysis

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
import joblib

Load data
df = pd.read_csv("twitter_training.csv", header=None)

Set custom headers because the dataset doesn't have headers
df.columns = ["ID", "Entity", "Sentiment", "Content"]

Remove the Indifferent and Irrelevant class
df["Sentiment"] = df["Sentiment"].apply(lambda x: 1 if x == "Positive" else 0)

Remove useless line
df = df.dropna(subset=["Sentiment", "Content"])

Train the dataset
X_train, X_test, y_train, y_test = train_test_split(
    df["Content"], df["Sentiment"], test_size=0.2, random_state=42
)

Vectorization step translats text to digit
model = Pipeline([
    ("tfidf", TfidfVectorizer(stop_words="english", max_features=100000)),
    ("clf", LogisticRegression(max_iter=1000))
])

model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

0       0.87      0.96      0.91     10681
           1       0.84      0.62      0.72      4119

    accuracy                           0.86     14800
   macro avg       0.86      0.79      0.81     14800
weighted avg       0.86      0.86      0.86     14800


joblib.dump(model, "sentiment_model.joblib")
'''
