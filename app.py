import os
import sys
import joblib
from flask import Flask, render_template, request, jsonify

# Include project base directory in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.nlp_pipeline import analyze_and_predict
from backend.db import init_db, save_prediction, get_history, get_analytics, delete_prediction, clear_history
from backend.sample_generator import SAMPLE_ARTICLES
from model.train_model import train_and_save_model

app = Flask(__name__, static_folder="static", template_folder="templates")

# Paths for ML artifacts
MODEL_PATH = os.path.join(BASE_DIR, "model", "fake_news_model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "model", "tfidf_vectorizer.pkl")

# Global variables for loaded model and vectorizer
model = None
vectorizer = None

def load_or_train_model():
    """Loads existing model artifacts or trains a new model if missing."""
    global model, vectorizer
    if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
        print("[App Startup] ML model artifacts not found. Training model now...")
        train_and_save_model()

    print("[App Startup] Loading ML model artifacts into memory...")
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    print("[App Startup] Model and Vectorizer loaded successfully!")

# Initialize Database and Load Model on Startup
with app.app_context():
    init_db()
    load_or_train_model()

@app.route("/")
def index():
    """Renders the main full-stack web interface."""
    return render_template("index.html")

@app.route("/api/predict", methods=["POST"])
def predict():
    """
    API Endpoint: Analyzes incoming news headline or article.
    Payload: { "text": "news article body or headline..." }
    """
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()

    if not text:
        return jsonify({
            "status": "error",
            "message": "Please provide a valid news headline or article text for analysis."
        }), 400

    if len(text) < 5:
        return jsonify({
            "status": "error",
            "message": "Input text is too short. Please enter a complete news headline or article."
        }), 400

    try:
        global model, vectorizer
        if model is None or vectorizer is None:
            load_or_train_model()

        result = analyze_and_predict(text, model, vectorizer)
        
        # Save prediction result to SQLite database
        pred_id = save_prediction(
            text=text,
            prediction=result["prediction"],
            confidence=result["confidence"],
            stats=result["stats"]
        )
        result["id"] = pred_id
        result["status"] = "success"

        return jsonify(result)

    except Exception as e:
        print(f"[App Error] Prediction error: {e}")
        return jsonify({
            "status": "error",
            "message": f"An error occurred during text analysis: {str(e)}"
        }), 500

@app.route("/api/history", methods=["GET"])
def history():
    """API Endpoint: Retrieves prediction history list with optional search query."""
    search_query = request.args.get("search", "")
    records = get_history(limit=100, search_query=search_query)
    return jsonify({
        "status": "success",
        "count": len(records),
        "history": records
    })

@app.route("/api/history/<int:pred_id>", methods=["DELETE"])
def delete_history_item(pred_id):
    """API Endpoint: Deletes a specific prediction item by ID."""
    success = delete_prediction(pred_id)
    if success:
        return jsonify({"status": "success", "message": f"Record #{pred_id} deleted successfully."})
    return jsonify({"status": "error", "message": f"Record #{pred_id} not found."}), 404

@app.route("/api/history", methods=["DELETE"])
def clear_all_history():
    """API Endpoint: Clears all history from SQLite database."""
    clear_history()
    return jsonify({"status": "success", "message": "Prediction history cleared successfully."})

@app.route("/api/stats", methods=["GET"])
def stats():
    """API Endpoint: Retrieves summary analytics metrics for dashboard."""
    analytics = get_analytics()
    return jsonify({
        "status": "success",
        "analytics": analytics
    })

@app.route("/api/samples", methods=["GET"])
def get_samples():
    """API Endpoint: Returns sample news articles for testing."""
    return jsonify({
        "status": "success",
        "samples": SAMPLE_ARTICLES
    })

@app.route("/api/retrain", methods=["POST"])
def retrain():
    """API Endpoint: Triggers model retraining."""
    try:
        res = train_and_save_model()
        load_or_train_model()
        return jsonify({
            "status": "success",
            "message": f"Model successfully retrained! Training accuracy: {res['accuracy']}%",
            "details": res
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    print("[App] Starting Flask server on http://127.0.0.1:5000...")
    app.run(host="127.0.0.1", port=5000, debug=True)
