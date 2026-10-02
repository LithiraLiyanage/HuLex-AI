import re
from statistics import pstdev

from sqlalchemy.orm import Session

from app.models.analysis_result import AnalysisResult
from app.models.document import Document


ROBOTIC_PHRASES = [
    "furthermore",
    "moreover",
    "it is important to note",
    "in conclusion",
    "therefore",
    "numerous",
    "significantly",
    "various",
    "utilize",
    "delve",
]


def _get_sentences(text: str) -> list[str]:
    return [
        sentence.strip()
        for sentence in re.split(r"[.!?]+", text)
        if sentence.strip()
    ]


def _get_words(text: str) -> list[str]:
    return re.findall(r"\b[a-zA-Z']+\b", text.lower())


def _estimate_syllables(word: str) -> int:
    word = word.lower()

    groups = re.findall(r"[aeiouy]+", word)

    count = max(1, len(groups))

    if word.endswith("e") and count > 1:
        count -= 1

    return max(1, count)


def calculate_readability(text: str) -> float:
    sentences = _get_sentences(text)
    words = _get_words(text)

    if not sentences or not words:
        return 0.0

    syllables = sum(_estimate_syllables(word) for word in words)

    score = (
        206.835
        - 1.015 * (len(words) / len(sentences))
        - 84.6 * (syllables / len(words))
    )

    return round(max(0.0, min(100.0, score)), 2)


def calculate_robotic_score(text: str) -> float:
    text_lower = text.lower()

    sentences = _get_sentences(text)
    words = _get_words(text)

    if not words:
        return 0.0

    phrase_hits = sum(
        text_lower.count(phrase)
        for phrase in ROBOTIC_PHRASES
    )

    phrase_score = min(
        60.0,
        phrase_hits * 12.0
    )

    sentence_lengths = [
        len(_get_words(sentence))
        for sentence in sentences
        if _get_words(sentence)
    ]

    uniformity_score = 0.0

    if len(sentence_lengths) >= 2:
        variation = pstdev(sentence_lengths)

        if variation < 2:
            uniformity_score = 20.0
        elif variation < 4:
            uniformity_score = 10.0

    long_sentence_score = 0.0

    average_length = (
        sum(sentence_lengths) / len(sentence_lengths)
        if sentence_lengths
        else 0
    )

    if average_length > 25:
        long_sentence_score = 20.0
    elif average_length > 18:
        long_sentence_score = 10.0

    score = (
        phrase_score
        + uniformity_score
        + long_sentence_score
    )

    return round(
        max(0.0, min(100.0, score)),
        2
    )


def detect_tone(text: str) -> str:
    text_lower = text.lower()

    conversational_words = [
        "i ",
        "you ",
        "we ",
        "don't",
        "can't",
        "it's",
    ]

    formal_words = [
        "furthermore",
        "therefore",
        "moreover",
        "significantly",
        "consequently",
    ]

    if any(word in text_lower for word in conversational_words):
        return "conversational"

    if any(word in text_lower for word in formal_words):
        return "formal"

    return "neutral"


def detect_audience(text: str) -> str:
    text_lower = text.lower()

    academic_terms = [
        "research",
        "study",
        "methodology",
        "analysis",
        "dataset",
        "experiment",
    ]

    professional_terms = [
        "organization",
        "business",
        "productivity",
        "customer",
        "management",
        "operational",
    ]

    if any(term in text_lower for term in academic_terms):
        return "academic"

    if any(term in text_lower for term in professional_terms):
        return "professional"

    return "general"


def analyze_document(
    db: Session,
    document: Document
) -> AnalysisResult:

    text = document.original_text

    readability = calculate_readability(text)
    robotic = calculate_robotic_score(text)
    naturalness = round(100.0 - robotic, 2)

    tone = detect_tone(text)
    audience = detect_audience(text)

    summary = (
        f"Detected {tone} tone for a {audience} audience. "
        f"Readability score: {readability}/100. "
        f"Naturalness score: {naturalness}/100. "
        f"Robotic-writing score: {robotic}/100."
    )

    result = AnalysisResult(
        document_id=document.id,
        detected_tone=tone,
        detected_audience=audience,
        readability_score=readability,
        naturalness_score=naturalness,
        robotic_score=robotic,
        semantic_score=None,
        analysis_summary=summary,
    )

    db.add(result)
    db.commit()
    db.refresh(result)

    return result