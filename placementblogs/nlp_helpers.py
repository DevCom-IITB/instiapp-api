import spacy
from spacy.matcher import PhraseMatcher
import re

# 1. Load the lightweight NLP model
nlp = spacy.load('en_core_web_sm')

# 2. Initialize the PhraseMatcher 
matcher = PhraseMatcher(nlp.vocab, attr="LEMMA")

# 3. Expanded Dictionary for Placement JAFs
DOMAIN_KEYWORDS = {
    'Software / IT': [
        'software', 'full stack', 'backend', 'frontend', 'flutter', 'django',
        'developer', 'sde', 'engineer 1', 'devops', 'cloud', 'systems', 'python',
        'digital twin', 'security', 'it analyst', 'technology trainee', 
        'technical support', 'blockchain', 'distributed ledger'
    ],
    'Data / AI & ML': [
        'data', 'ai', 'ml', 'machine learning', 'artificial intelligence', 
        'llm', 'computer vision', 'data scientist', 'data science', 'genai'
    ],
    'Analytics': [
        'analyst', 'analytics', 'business analytics'
    ],
    'Quant / Finance': [
        'finance', 'investment', 'banking', 'quant', 'trading', 'dealer', 
        'securities', 'quantitative', 'vc', 'private equity'
    ],
    'Consulting': [
        'consultant', 'consulting'
    ],
    'Management / Operations': [
        'management trainee', 'mt', 'ylp', 'manager', 'associate', 
        'program manager', 'executive', 'business development', 'ceo', 
        'strategy', 'ops', 'operations', 'category', 'supply chain', 'logistics',
        'graduate trainee', 'techno commercial', 'business innovation'
    ],
    'Research & Development': [
        'research', 'scientist', 'r&d', 'researcher', 'geology', 'geophysics', 
        'chemistry', 'scientific', 'applied scientist'
    ],
    'Design (UI/UX / Product)': [
        'design', 'designer', 'ui/ux', 'ui', 'ux', 'creative', 'graphics', 
        'visual designer', 'visual design', 'product', 'industrial designer'
    ],
    'Education / Teaching': [
        'faculty', 'professor', 'content writer', 'teacher', 'instructor'
    ],
    'Core Engineering': [
        'robotics', 'uav', 'autonomous', 'get', 'graduate engineer trainee', 
        'electrical', 'civil', 'mechanical', 'mechatronics', 'structures',
        'process engineering', 'process validation', 'water resources', 
        'hydrology', 'gis', 'safety', 'b.e', 'b.tech', 'hardware', 'pde', 'simulation',
        'project engineer', 'trainee engineer', 'pgte', 'post graduate trainee',
        'probationary engineer', 'silicon', 'gnc', 'industrial engineering', 
        'production', 'young engineering'
    ]
}

# 4. Compile the patterns into the matcher once
for domain, terms in DOMAIN_KEYWORDS.items():
    patterns = list(nlp.pipe(terms))
    matcher.add(domain, patterns)

def infer_domain(role_text: str) -> str:
    """
    Reads the job role, filters out HTML garbage, cleans punctuation, 
    analyzes the grammar, and returns the closest domain.
    """
    if not role_text:
        return "[UNMATCHED]"

    # Clean the input
    role_text = role_text.lower().strip()
    
    # --- 1. THE GARBAGE FILTER ---
    if len(role_text) <= 3 or 'roll no' in role_text or 'link' in role_text or 'start' in role_text or '|' in role_text or 'shortlist' in role_text:
        return '[GARBAGE / IGNORE]'

    # --- 2. PUNCTUATION & ARTIFACT SCRUBBER ---
    # Replaces dashes, underscores, and brackets with spaces so spaCy can read words separately 
    # Example: "Researcher(IDC)" becomes "Researcher IDC"
    role_text = re.sub(r'[_\-\–\(\)]', ' ', role_text)
    
    # Removes lingering "Job code 1 :" artifacts that might confuse the matcher
    role_text = re.sub(r'job\s*code\s*\d+\s*[:]*\s*', '', role_text)

    # --- 3. NLP PROCESSING ---
    doc = nlp(role_text)
    matches = matcher(doc)
    
    if matches:
        match_id, start, end = matches[0]
        best_domain = nlp.vocab.strings[match_id]
        return best_domain
        
    return "General"