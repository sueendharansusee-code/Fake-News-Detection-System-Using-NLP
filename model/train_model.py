import os
import sys
import argparse
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

# Add parent directory to sys.path to allow imports from backend
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.nlp_pipeline import preprocess_text
from backend.sample_generator import generate_sample_dataset

def train_and_save_model(data_path=None, model_dir=None):
    """
    Trains TF-IDF + Logistic Regression model on specified dataset and saves pickle files.
    """
    if model_dir is None:
        model_dir = os.path.join(BASE_DIR, "model")
    os.makedirs(model_dir, exist_ok=True)

    if data_path is None:
        data_path = os.path.join(BASE_DIR, "data", "sample_news.csv")

    if not os.path.exists(data_path):
        print(f"[Trainer] Dataset not found at '{data_path}'. Generating default sample dataset...")
        generate_sample_dataset(data_path)

    print(f"[Trainer] Loading dataset from: {data_path}")
    df = pd.read_csv(data_path)

    # Ensure required columns exist
    if 'text' not in df.columns or 'label' not in df.columns:
        raise ValueError(f"Dataset at {data_path} must contain 'text' and 'label' columns.")

    df = df.dropna(subset=['text', 'label'])

    print(f"[Trainer] Preprocessing {len(df)} samples...")
    processed_texts = []
    for text in df['text']:
        clean_text, _ = preprocess_text(str(text))
        processed_texts.append(clean_text)

    # Normalize labels to 'REAL' and 'FAKE'
    labels = []
    for lbl in df['label']:
        lbl_str = str(lbl).strip().upper()
        if lbl_str in ['1', 'REAL', 'TRUE', 'FACTUAL']:
            labels.append('REAL')
        else:
            labels.append('FAKE')

    # Fit TF-IDF Vectorizer
    print("[Trainer] Fitting TF-IDF Vectorizer...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=5000,
        sublinear_tf=True
    )
    X = vectorizer.fit_transform(processed_texts)
    y = labels

    # Train Logistic Regression Model
    print("[Trainer] Training Logistic Regression Classifier...")
    model = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
    model.fit(X, y)

    # Evaluation
    y_pred = model.predict(X)
    acc = accuracy_score(y, y_pred)
    print(f"[Trainer] Model Training Accuracy: {acc * 100:.2f}%")
    print("[Trainer] Classification Report:\n", classification_report(y, y_pred))

    # Save artifacts
    model_path = os.path.join(model_dir, "fake_news_model.pkl")
    vectorizer_path = os.path.join(model_dir, "tfidf_vectorizer.pkl")

    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)

    print(f"[Trainer] Model saved to: {model_path}")
    print(f"[Trainer] Vectorizer saved to: {vectorizer_path}")

    return {
        "accuracy": round(float(acc) * 100, 2),
        "total_samples": len(df),
        "model_path": model_path,
        "vectorizer_path": vectorizer_path
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Fake News Detection NLP Model")
    parser.add_argument("--data", type=str, default=None, help="Path to input dataset CSV")
    parser.add_argument("--model-dir", type=str, default=None, help="Directory to save model artifacts")
    args = parser.parse_args()

    train_and_save_model(data_path=args.data, model_dir=args.model_dir)
