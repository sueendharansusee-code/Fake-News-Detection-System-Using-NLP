import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Ensure NLTK data dependencies are loaded safely
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    try:
        nltk.download('stopwords', quiet=True)
    except Exception as e:
        print(f"[NLP Pipeline] Warning downloading NLTK stopwords: {e}")

# Fallback basic stopwords list in case NLTK download is blocked or fails
FALLBACK_STOPWORDS = set([
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours",
    "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers",
    "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves",
    "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does",
    "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until",
    "while", "of", "at", "by", "for", "with", "about", "against", "between", "into",
    "through", "during", "before", "after", "above", "below", "to", "from", "up", "down",
    "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so",
    "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"
])

def get_stopwords():
    try:
        return set(stopwords.words('english'))
    except Exception:
        return FALLBACK_STOPWORDS

stemmer = PorterStemmer()

def preprocess_text(text):
    """
    NLP Preprocessing pipeline:
    1. Lowercase text
    2. Remove URLs, HTML tags, and numbers
    3. Remove punctuation
    4. Tokenize
    5. Remove Stopwords
    6. Apply Stemming
    """
    if not text or not isinstance(text, str):
        return "", []

    # 1. Lowercase
    text_lower = text.lower()

    # 2. Clean URLs, HTML tags, digits
    text_clean = re.sub(r'https?://\S+|www\.\S+', '', text_lower)
    text_clean = re.sub(r'<.*?>', '', text_clean)
    text_clean = re.sub(r'\d+', '', text_clean)

    # 3. Remove punctuation
    text_clean = text_clean.translate(str.maketrans('', '', string.punctuation))

    # 4. Tokenization
    raw_tokens = text_clean.split()

    # 5. Remove Stopwords & Stemming
    sw = get_stopwords()
    clean_tokens = [stemmer.stem(word) for word in raw_tokens if word not in sw and len(word) > 1]

    processed_string = " ".join(clean_tokens)
    return processed_string, clean_tokens

def extract_text_stats(original_text, processed_string):
    """
    Computes text statistics comparing raw input vs preprocessed input.
    """
    original_words = original_text.split() if original_text else []
    processed_tokens = processed_string.split() if processed_string else []

    word_count = len(original_words)
    char_count = len(original_text) if original_text else 0
    sw = get_stopwords()
    
    stopword_count = sum(1 for w in original_words if w.lower().strip(string.punctuation) in sw)
    unique_words = len(set(processed_tokens))
    
    lexical_diversity = round((unique_words / max(word_count, 1)) * 100, 1)

    return {
        "word_count": word_count,
        "char_count": char_count,
        "stopword_count": stopword_count,
        "unique_words": unique_words,
        "lexical_diversity_pct": lexical_diversity,
        "clean_token_count": len(processed_tokens)
    }

def analyze_and_predict(text, model, vectorizer):
    """
    Analyzes news input through preprocessing, vectorization, and model inference.
    Returns structured results dictionary.
    """
    clean_text, tokens = preprocess_text(text)
    stats = extract_text_stats(text, clean_text)

    # If clean text is empty (e.g. only punctuation or stopwords), return fallback
    if not clean_text.strip():
        return {
            "prediction": "UNKNOWN",
            "confidence": 50.0,
            "probabilities": {"REAL": 0.5, "FAKE": 0.5},
            "stats": stats,
            "processed_text": "",
            "warning": "Input contained insufficient informative text after preprocessing."
        }

    # Vectorize
    vectorized = vectorizer.transform([clean_text])

    # Predict class & probability
    prediction_label = model.predict(vectorized)[0] # Could be 0/1 or 'FAKE'/'REAL'
    probabilities = model.predict_proba(vectorized)[0] # [prob_0, prob_1]

    # Model classes mapping
    classes = list(model.classes_)
    prob_dict = {}
    for idx, cls_name in enumerate(classes):
        label_str = "REAL" if str(cls_name).upper() in ["1", "REAL", "TRUE"] else "FAKE"
        prob_dict[label_str] = round(float(probabilities[idx]) * 100, 2)

    # Resolve normalized prediction string
    prediction_str = "REAL" if str(prediction_label).upper() in ["1", "REAL", "TRUE"] else "FAKE"
    confidence = prob_dict.get(prediction_str, round(float(max(probabilities)) * 100, 2))

    return {
        "prediction": prediction_str,
        "confidence": confidence,
        "probabilities": prob_dict,
        "stats": stats,
        "processed_text": clean_text
    }
