import joblib 
import os 

MODEL_PATH = os.path.join(os.path.dirname(__file__), "ml", "sentiment_dt_tfidf.joblib") 
_model = joblib.load(MODEL_PATH) 

def analyze_sentiment(message: str): 
    """ Retourne un dict {"label": "Positive"/"Negative", "proba": float|None} """ 
    if not message or not message.strip(): return {"label": None, "proba": None} 
    
# prédiction sur texte brut : le pipeline applique TF-IDF puis l'arbre 
label = _model.predict([message])[0] 
    
# définition de la proba en binaire: 
def analyze_sentiment_binary(message: str) -> int: 
    res = analyze_sentiment(message) 
    return 1 if res["label"] == "Positive" else 0



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

    1. load dataset
        df = pd.read_csv("twitter_training.csv")
        df.columns = ["ID", "Entity", "Sentiment", "Content"]
        df.head()

    2. clean and preprocess
        print(df.isna().sum())
        df.describe()
        df = df.dropna(subset=["Sentiment", "Content"])
        df = df[df["Sentiment"].isin(["Positive", "Negative"])]
        print("\nShape après filtrage:", df.shape)
        print(df["Sentiment"].value_counts())

    3. split dataset
        y = df["Sentiment"]
        X = df["Content"].astype(str)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y) #stratifier pr garder le ratio positif/négatif identique entre train et test
        print("\nTaille du jeu d'entraînement:", X_train.shape)
        print("Taille du jeu de test:", X_test.shape)

    4. build/train/evaluate (Logistic/DecissionTree/RandomForest)
       
        === Logistic Regression === accuracy à 0.8888
        clf1 = Pipeline(steps=[
            ("tfidf", TfidfVectorizer(max_features=20000, stop_words="english", ngram_range=(1,2))),
            ("logreg", LogisticRegression(max_iter=1000))
        ])
        clf1.fit(X_train, y_train)
        y_pred1 = clf1.predict(X_test)
        print("\n=== Logistic Regression ===")
        print("Accuracy:", accuracy_score(y_test, y_pred1))
        print(classification_report(y_test, y_pred1))
        
        === Decision Tree === plus long mais accuracy à 0.8912
        clf2 = Pipeline(steps=[
            ("tfidf", TfidfVectorizer(max_features=20000, stop_words="english", ngram_range=(1,2))),
            ("tree", DecisionTreeClassifier(random_state=42))
        ])
        clf2.fit(X_train, y_train)
        y_pred2 = clf2.predict(X_test)
        print("\n=== Decision Tree ===")
        print("Accuracy:", accuracy_score(y_test, y_pred2))
        print(classification_report(y_test, y_pred2))
        >>> résultats : 
            === Decision Tree ===
            Accuracy: 0.8912007439265373
                        precision    recall  f1-score   support
                Negative       0.91      0.88      0.89      4472
                Positive       0.87      0.90      0.89      4131
                accuracy                           0.89      8603
            macro avg       0.89      0.89      0.89      8603
            weighted avg       0.89      0.89      0.89      8603
        
        === Random Forest : accuracy à 0.94 mais très long, non adapté aux données types "commentaires"=== 
        clf3 = Pipeline(steps=[
            ("tfidf", TfidfVectorizer(max_features=20000, stop_words="english", ngram_range=(1,2))),
            ("forest", RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1))
        ])
        clf3.fit(X_train, y_train)
        y_pred3 = clf3.predict(X_test)
        print("\n=== Random Forest ===")
        print("Accuracy:", accuracy_score(y_test, y_pred3))
        print(classification_report(y_test, y_pred3))

    >>> Keeping Decision Tree for balance between performance and training time. Features importance visualization:
        vec2 = clf2.named_steps["tfidf"]
        tree = clf2.named_steps["tree"]
        importances = tree.feature_importances_
        feature_names = np.array(vec2.get_feature_names_out())
        mask = importances > 0
        importances = importances[mask]
        feature_names = feature_names[mask]
        if importances.size == 0:
            print("Aucune importance non nulle trouvée pour l'arbre (feature_importances_ toutes à 0).")
        else:
            top_idx = np.argsort(importances)[-20:][::-1]
            plt.figure(figsize=(10,6))
            plt.barh(feature_names[top_idx][::-1], importances[top_idx][::-1])
            plt.title("Top 20 termes les plus importants (Decision Tree)")
            plt.xlabel("Importance (feature_importances_)")
            plt.tight_layout()
            plt.show()

    6. save trained model
        dump(clf2, "sentiment_decision_tree_model.joblib")
        print("Modèle sauvegardé sous 'sentiment_decision_tree_model.joblib'")
"""