
from functools import lru_cache
from pathlib import Path

import joblib


PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_PATH = (
    PROJECT_ROOT
    / "ai-models"
    / "human-ai-detector"
    / "artifacts"
    / "human_ai_classifier.joblib"
)


@lru_cache(maxsize=1)
def load_detector():
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"Trained ML model not found: {MODEL_PATH}"
        )

    # Only load model artifacts created by our own training code.
    return joblib.load(MODEL_PATH)


def detect_ai_text(text: str) -> dict:
    text = text.strip()

    if len(text.split()) < 30:
        raise ValueError(
            "Please provide at least 30 words for analysis."
        )

    model = load_detector()

    probabilities = model.predict_proba([text])[0]

    class_probabilities = dict(
        zip(model.classes_, probabilities)
    )

    human_score = float(class_probabilities[0])
    ai_score = float(class_probabilities[1])

    predicted_label = (
        "AI-like" if ai_score >= 0.5 else "Human-like"
    )

    return {
        "predicted_label": predicted_label,
        "ai_likelihood": round(ai_score, 4),
        "human_likelihood": round(human_score, 4),
        "model": "TF-IDF + Logistic Regression",
        "warning": (
            "Scores reflect patterns learned from the "
            "training dataset. They do not prove authorship."
        ),
    }
