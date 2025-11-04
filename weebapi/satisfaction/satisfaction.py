import joblib
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "sentiment_model.joblib")
model = joblib.load(MODEL_PATH)


def analyze_satisfaction(message):
    """
    Analyze the satisfaction (sentiment) of a given message.

    Uses a pre-trained logistic regression text classification model
    to determine whether a message expresses positive or negative sentiment.

    The model was trained on a dataset derived from Twitter sentiment analysis.
    A positive sentiment returns `1`, while a negative (or neutral) sentiment
    returns `0`.

    Args:
        message (str): The input message text to analyze.

    Returns:
        int: 1 if the message is predicted as positive, 0 otherwise.
             Returns 0 if the message is empty or only contains whitespace.
    """
    if not message or len(message.strip()) == 0:
        return 0
    prediction = model.predict([message])
    return int(prediction[0])


"""
Model Training Notes
--------------------

Dataset:
    Source:
        https://www.kaggle.com/datasets/jp797498e/twitter-entity-sentiment-analysis
    Description:
        A labeled dataset of Twitter posts containing entities and sentiment
        labels.

Training Steps:
    1. Load dataset
        >>> import pandas as pd
        >>> df = pd.read_csv("twitter_training.csv", header=None)
        >>> df.columns = ["ID", "Entity", "Sentiment", "Content"]

    2. Clean and preprocess
        - Keep only 'Positive' and 'Negative' samples.
        - Convert sentiment labels to binary:
            Positive → 1, Negative → 0
        >>> df["Sentiment"] = df["Sentiment"].apply(
        lambda x: 1 if x == "Positive" else 0)
        >>> df = df.dropna(subset=["Sentiment", "Content"])

    3. Split dataset
        >>> from sklearn.model_selection import train_test_split
        >>> X_train, X_test, y_train, y_test = train_test_split(
        ...     df["Content"], df["Sentiment"], test_size=0.2, random_state=42
        ... )

    4. Build and train model
        >>> from sklearn.feature_extraction.text import TfidfVectorizer
        >>> from sklearn.linear_model import LogisticRegression
        >>> from sklearn.pipeline import Pipeline
        >>> model = Pipeline([
        ...     ("tfidf", TfidfVectorizer(stop_words="english",
                max_features=100000)),
        ...     ("clf", LogisticRegression(max_iter=1000))
        ... ])
        >>> model.fit(X_train, y_train)

    5. Evaluate
        >>> from sklearn.metrics import classification_report
        >>> y_pred = model.predict(X_test)
        >>> print(classification_report(y_test, y_pred))

        Results (example):
            precision    recall  f1-score   support
            0       0.87      0.96      0.91     10681
            1       0.84      0.62      0.72      4119
            accuracy                           0.86     14800
            macro avg       0.86      0.79      0.81     14800
            weighted avg    0.86      0.86      0.86     14800

    6. Save trained model
        >>> import joblib
        >>> joblib.dump(model, "sentiment_model.joblib")
"""
