import os
import joblib


# Path to the pre-trained sentiment analysis model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "sentiment_model.joblib")
_model = joblib.load(MODEL_PATH)


def analyze_satisfaction(message: str) -> dict:
    """Analyze the sentiment of a message and return the result.

    This function uses a pre-trained text classification model
    (TF-IDF + Random Forest) to predict whether the sentiment
    of a given message is positive or negative.

    Args:
        message (str): The input text message to analyze.

    Returns:
        dict: A dictionary containing:
            - label (str | None): "Positive" or "Negative", or None if
              input is empty.
            - proba (float | None): Reserved for future probability use.
    """
    if not message or not message.strip():
        return {"label": None, "proba": None}

    # Predict sentiment from raw text (TF-IDF + Random Forest)
    label = _model.predict([message])[0]
    return {"label": label, "proba": None}


def analyze_satisfaction_binary(message: str) -> int:
    """Analyze sentiment and return a binary label.

    Args:
        message (str): The text to analyze.

    Returns:
        int: 1 if sentiment is positive, 0 otherwise.
    """
    result = analyze_satisfaction(message)
    return 1 if result["label"] == "Positive" else 0


"""
Model Training Notes
--------------------

Dataset
--------
Source:
    https://www.kaggle.com/datasets/jp797498e/twitter-entity-sentiment-analysis

Description:
    A labeled dataset of Twitter posts containing entities and sentiment
    labels.

Training Steps
--------------
1. Load dataset
    df = pd.read_csv("twitter_training.csv", header=None)
    df.columns = ["ID", "Entity", "Sentiment", "Content"]
    df.head()

2. Clean and preprocess
    print(df.isna().sum())
    df.describe()
    df = df.dropna(subset=["Sentiment", "Content"])
    df = df[df["Sentiment"].isin(["Positive", "Negative"])]
    print("\nShape after filtering:", df.shape)
    print(df["Sentiment"].value_counts())

3. Split dataset
    y = df["Sentiment"]
    X = df["Content"].astype(str)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )  # Stratify to preserve class ratio
    print("\nTraining set size:", X_train.shape)
    print("Test set size:", X_test.shape)

4. Build / Train / Evaluate models

    === Logistic Regression (accuracy ≈ 0.92) ===
    clf1 = Pipeline(steps=[
        ("tfidf", TfidfVectorizer(max_features=100000, stop_words="english",
        ngram_range=(1, 2))),
        ("logreg", LogisticRegression(max_iter=1000))
    ])
    clf1.fit(X_train, y_train)
    y_pred1 = clf1.predict(X_test)
    print("\n=== Logistic Regression ===")
    print("Accuracy:", accuracy_score(y_test, y_pred1))
    print(classification_report(y_test, y_pred1))

    === Decision Tree (accuracy ≈ 0.89) ===
    clf2 = Pipeline(steps=[
        ("tfidf", TfidfVectorizer(max_features=100000, stop_words="english",
        ngram_range=(1, 2))),
        ("tree", DecisionTreeClassifier(random_state=42))
    ])
    clf2.fit(X_train, y_train)
    y_pred2 = clf2.predict(X_test)
    print("\n=== Decision Tree ===")
    print("Accuracy:", accuracy_score(y_test, y_pred2))
    print(classification_report(y_test, y_pred2))

    === Random Forest (accuracy ≈ 0.94, chosen model) ===
    clf3 = Pipeline(steps=[
        ("tfidf", TfidfVectorizer(max_features=100000, stop_words="english",
        ngram_range=(1, 2))),
        ("forest", RandomForestClassifier(n_estimators=200, random_state=42,
        n_jobs=-1))
    ])
    clf3.fit(X_train, y_train)
    y_pred3 = clf3.predict(X_test)
    print("\n=== Random Forest ===")
    print("Accuracy:", accuracy_score(y_test, y_pred3))
    print(classification_report(y_test, y_pred3))

5. Save the trained model
    dump(clf3, "sentiment_model.joblib")
    print("Model saved as 'sentiment_model.joblib'")
"""
