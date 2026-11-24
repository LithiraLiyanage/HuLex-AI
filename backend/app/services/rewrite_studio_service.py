"""Safe, minimally invasive polish and optional configured language-model rewriting.

No false claims of semantic preservation: meaningful semantic evaluation must be
implemented and evaluated separately. Keys are read server-side only.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

# Read values in backend/.env without changing the existing pydantic settings model.
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / '.env', override=False)
except ImportError:
    pass


RULES = (
    (r'\bIt is important to note that\s+', ''),
    (r'\bit should be noted that\s+', ''),
    (r'\bdue to the fact that\b', 'because'),
    (r'\bin order to\b', 'to'),
    (r'\bwith regard to\b', 'about'),
    (r'\bprior to\b', 'before'),
    (r'\bsubsequent to\b', 'after'),
    (r'\ba significant number of\b', 'many'),
    (r'\bat this point in time\b', 'now'),
    (r'\bthe utilization of\b', 'using'),
    (r'\butilize\b', 'use'),
    (r'\butilizing\b', 'using'),
)


def local_polish(text: str, tone: str, length: str) -> str:
    """Deterministic substitutions only; not a neural rewrite or semantic guarantee."""
    result = text
    for pattern, replacement in RULES:
        # Retain capitalization at sentence starts where possible.
        def replace(match: re.Match[str]) -> str:
            value = replacement
            if value and match.group()[0].isupper():
                value = value[0].upper() + value[1:]
            return value
        result = re.sub(pattern, replace, result, flags=re.IGNORECASE)
    result = re.sub(r'[ \t]{2,}', ' ', result).strip()
    result = re.sub(r'(?m)^[a-z]', lambda m: m.group().upper(), result)
    return result


def _llm_rewrite(text: str, tone: str, length: str, key: str) -> str:
    url = os.getenv('HULEX_REWRITE_URL', 'https://api.openai.com/v1/chat/completions')
    model = os.getenv('HULEX_REWRITE_MODEL', 'gpt-4o-mini')
    if not url.startswith('https://'):
        raise ValueError('HULEX_REWRITE_URL must be an HTTPS endpoint.')
    instructions = (
        'You are a careful professional writing editor. Rewrite the provided text '
        f'in a {tone.lower()} tone with {length.lower()} length. '
        'Preserve the author\'s intended meaning, specific claims, numbers, dates, '
        'names, citations, and uncertainty. Never invent facts or quotations. '
        'Do not add information not provided. Return only the rewritten text. '
        'Do not mention AI detection or try to manipulate detection tools.'
    )
    payload = json.dumps({
        'model': model,
        'temperature': 0.35,
        'messages': [
            {'role': 'system', 'content': instructions},
            {'role': 'user', 'content': text},
        ],
    }).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=payload,
        headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as res:
            output = json.load(res)
    except urllib.error.HTTPError as err:
        raise RuntimeError(f'Writing model provider returned HTTP {err.code}. Check your key and model.') from err
    except (urllib.error.URLError, TimeoutError) as err:
        raise RuntimeError('Could not reach the configured writing model.') from err

    try:
        rewritten = output['choices'][0]['message']['content'].strip()
    except (KeyError, IndexError, TypeError, AttributeError) as err:
        raise RuntimeError('Writing model returned an unexpected response.') from err
    if not rewritten:
        raise RuntimeError('Writing model returned empty text.')
    return rewritten


def refine_text(text: str, tone: str, length: str) -> dict:
    key = os.getenv('HULEX_REWRITE_API_KEY') or os.getenv('OPENAI_API_KEY')
    if key:
        return {
            'rewritten_text': _llm_rewrite(text, tone, length, key),
            'mode': 'model_rewrite',
            'notes': 'Rewritten with the configured model. Review facts and meaning before use.',
        }
    output = local_polish(text, tone, length)
    return {
        'rewritten_text': output,
        'mode': 'local_polish',
        'notes': (
            'Basic offline phrasing cleanup only. Tone and length controls require '
            'a configured model. The output has not been semantically validated.'
        ),
    }
