import spacy
from spacy.matcher import PhraseMatcher

DOMAIN_KEYWORDS = {
    'Software': [
        'software', 'full stack', 'backend', 'frontend', 'flutter',
        'developer', 'engineer', 'devops', 'cloud', 'ml', 'ai',
        'data scientist', 'data science', 'data science intern', 'vr',
        'product', 'qa', 'applied scientist', 'it analyst', 'sds',
        'python', 'pyspark', 'systems', 'engineering analyst'
    ],
    'Finance': [
        'finance', 'investment', 'banking', 'quant', 'trading',
        'strategy', 'financial analyst', 'finance analyst',
        'investment analyst', 'real estate', 'quantitative',
        'venture capital', 'vc', 'private equity'
    ],
    'Research': [
        'research', 'modeling', 'geology', 'geophysics', 'material',
        'chemistry', 'environmental', 'scientific', 'surf'
    ],
    'Design': [
        'design', 'ux', 'ui', 'creative', 'graphics',
        'visual designer', 'visual design'
    ],
    'Operations': [
        'operations', 'supply chain', 'logistics',
        'project', 'trainee'
    ],
    'Marketing': [
        'marketing', 'market research',
        'business strategy', 'growth'
    ],
    'Core': [
        'robotics', 'uav', 'autonomous', 'get', 'electrical',
        'pde', 'simulation', 'electronics', 'instrumentation',
        'prototype', 'modeling', 'technical intern'
    ],
}

_nlp = None
_matcher = None


def _initialize():
    """
    Lazily load the spaCy model and build the PhraseMatcher.
    Runs only once.
    """
    global _nlp, _matcher

    if _nlp is not None:
        return

    _nlp = spacy.load("en_core_web_sm")
    _matcher = PhraseMatcher(_nlp.vocab, attr="LEMMA")

    for domain, terms in DOMAIN_KEYWORDS.items():
        patterns = list(_nlp.pipe(terms))
        _matcher.add(domain, patterns)


def infer_domain(role_text: str) -> str:
    """
    Reads the job role and returns the closest domain.
    """
    if not role_text:
        return ""

    _initialize()

    doc = _nlp(role_text.lower())
    matches = _matcher(doc)

    if matches:
        match_id, start, end = matches[0]
        return _nlp.vocab.strings[match_id]

    return ""