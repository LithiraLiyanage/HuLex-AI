
from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
)

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = BASE_DIR / "data" / "dataset.csv"
MODEL_PATH = BASE_DIR / "artifacts" / "human_ai_classifier.joblib"
EVAL_DIR = BASE_DIR / "evaluation"


def load_dataset():
    df = pd.read_csv(DATA_PATH)

    required = {"text", "label", "group_id"}
    if not required.issubset(df.columns):
        raise ValueError(
            "CSV must contain text, label, and group_id columns."
        )

    df = df[["text", "label", "group_id"]].dropna().copy()

    df["text"] = df["text"].astype(str).str.strip()
    df["label"] = pd.to_numeric(df["label"], errors="coerce")

    df = df[
        (df["text"].str.len() >= 20)
        & (df["label"].isin([0, 1]))
    ].copy()

    df = df.drop_duplicates(subset=["text"])
    df["label"] = df["label"].astype(int)

    if df["group_id"].nunique() < 10:
        raise ValueError("Not enough unique question groups.")

    if set(df["label"].unique()) != {0, 1}:
        raise ValueError("Both Human and AI labels are required.")

    return df


def build_model():
    features = FeatureUnion([
        (
            "word_tfidf",
            TfidfVectorizer(
                analyzer="word",
                ngram_range=(1, 2),
                max_features=50000,
                min_df=2,
                sublinear_tf=True,
            ),
        ),
        (
            "char_tfidf",
            TfidfVectorizer(
                analyzer="char_wb",
                ngram_range=(3, 5),
                max_features=30000,
                min_df=2,
                sublinear_tf=True,
            ),
        ),
    ])

    return Pipeline([
        ("features", features),
        (
            "classifier",
            LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=42,
            ),
        ),
    ])


def main():
    print("Loading HC3 dataset...")
    df = load_dataset()

    print("Total samples:", len(df))
    print("Question groups:", df["group_id"].nunique())
    print("Label distribution:")
    print(df["label"].value_counts())

    # Keep answers to the same question in one split.
    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=0.20,
        random_state=42,
    )

    train_idx, test_idx = next(
        splitter.split(
            df["text"],
            df["label"],
            groups=df["group_id"],
        )
    )

    train_df = df.iloc[train_idx]
    test_df = df.iloc[test_idx]

    train_groups = set(train_df["group_id"])
    test_groups = set(test_df["group_id"])

    assert train_groups.isdisjoint(test_groups)

    X_train = train_df["text"]
    y_train = train_df["label"]

    X_test = test_df["text"]
    y_test = test_df["label"]

    print("\nTrain samples:", len(train_df))
    print("Test samples:", len(test_df))
    print("Group leakage: NONE")

    print("\nTraining TF-IDF + Logistic Regression...")

    model = build_model()
    model.fit(X_train, y_train)

    print("Training complete!")

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(
            precision_score(y_test, predictions, zero_division=0)
        ),
        "recall": float(
            recall_score(y_test, predictions, zero_division=0)
        ),
        "f1_score": float(
            f1_score(y_test, predictions, zero_division=0)
        ),
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
        "train_samples": int(len(train_df)),
        "test_samples": int(len(test_df)),
        "train_groups": int(len(train_groups)),
        "test_groups": int(len(test_groups)),
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVAL_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_PATH)

    with open(
        EVAL_DIR / "metrics.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(metrics, file, indent=4)

    report = classification_report(
        y_test,
        predictions,
        labels=[0, 1],
        target_names=["Human", "AI"],
        zero_division=0,
    )

    with open(
        EVAL_DIR / "classification_report.txt",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(report)

    cm = confusion_matrix(
        y_test,
        predictions,
        labels=[0, 1],
    )

    pd.DataFrame(
        cm,
        index=["Actual Human", "Actual AI"],
        columns=["Predicted Human", "Predicted AI"],
    ).to_csv(EVAL_DIR / "confusion_matrix.csv")

    print("\n========== RESULTS ==========")

    for name, value in metrics.items():
        if name in {
            "accuracy", "precision", "recall",
            "f1_score", "roc_auc"
        }:
            print(f"{name}: {value:.4f}")

    print("\nClassification Report:")
    print(report)

    print("\nModel saved:", MODEL_PATH)
    print("Evaluation saved:", EVAL_DIR)


if __name__ == "__main__":
    main()
