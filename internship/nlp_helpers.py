import spacy
from spacy.matcher import PhraseMatcher

# 1. Load the lightweight NLP model
nlp = spacy.load('en_core_web_sm')

# 2. Initialize the PhraseMatcher to match on 'LEMMA' (base words)
# This means 'developer' will also automatically match 'developers' or 'development'
matcher = PhraseMatcher(nlp.vocab, attr="LEMMA")

DOMAIN_KEYWORDS = {
    'Software':    ['software', 'full stack', 'backend', 'frontend', 'flutter',
                    'developer', 'engineer', 'devops', 'cloud', 'ml', 'ai',
                    'data scientist', 'data science', 'data science intern', 'vr', 
                    'product', 'qa', 'applied scientist', 'it analyst', 'sds', 
                    'python', 'pyspark', 'systems', 'engineering analyst'],
    'Finance':     ['finance', 'investment', 'banking', 'quant', 'trading',
                    'strategy', 'financial analyst', 'finance analyst', 
                    'investment analyst', 'real estate', 'quantitative', 'quant', 
                    'venture capital', 'vc', 'private equity'],
    'Research':    ['research', 'modeling', 'geology', 'geophysics', 'material',
                    'chemistry', 'environmental', 'scientific', 'surf'],
    'Design':      ['design', 'ux', 'ui', 'creative', 'graphics', 'visual designer', 
                    'visual design'],
    'Operations':  ['operations', 'supply chain', 'logistics', 'project', 'trainee'],
    'Marketing':   ['marketing', 'market research', 'business strategy', 'growth'],
    'Core':        ['robotics', 'uav', 'autonomous', 'get', 'electrical', 'pde', 
                    'simulation', 'electronics', 'instrumentation', 'prototype', 
                    'modeling', 'technical intern'],
}

# 3. Compile the patterns into the matcher once (makes it blazing fast)
for domain, terms in DOMAIN_KEYWORDS.items():
    # We create spaCy docs for each term and add them to the matcher under the domain name
    patterns = list(nlp.pipe(terms))
    matcher.add(domain, patterns)

def infer_domain(role_text: str) -> str:
    """
    Reads the job role, analyzes the grammar, and returns the closest domain.
    """
    if not role_text:
        return ""

    # Process the text
    doc = nlp(role_text.lower())
    
    # Run the matcher
    matches = matcher(doc)
    
    if matches:
        # matches returns a list of tuples: (match_id, start, end)
        # We grab the first match and convert the ID back to the string (e.g., 'Software')
        match_id, start, end = matches[0]
        best_domain = nlp.vocab.strings[match_id]
        return best_domain
        
    return "" # Leave blank for future LLM fallback