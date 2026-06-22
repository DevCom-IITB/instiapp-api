import json
import re
import html  
from nlp_helpers import infer_domain

file_path = 'internship_blog_last500.json'

with open(file_path, 'r', encoding='utf-8') as f:
    feed_data = json.load(f)
    
posts = feed_data if isinstance(feed_data, list) else feed_data.get('items', [])

print(f"\n--- RUNNING SPACY NLP DOMAIN TEST ---\n")
print(f"{'COMPANY':<25} | {'ROLE EXTRACTED':<35} | {'INFERRED DOMAIN'}")
print("-" * 80)

match_count = 0
unmatched_count = 0

for post in posts:
    title = post.get('title', '')
    
    # Only process IAF Open posts
    if 'IAF OPEN' not in title.upper():
        continue
        
    content = post.get('content', '')
    
    # Grab the Profile/Role from the HTML
    role_match = re.search(r'Profile\b[^:]*:\s*([^<]+)', content, re.IGNORECASE)
    role = role_match.group(1).strip() if role_match else ""
    role = html.unescape(role).replace('\xa0', ' ').lower()
    # Run it through your new spaCy engine!
    domain = infer_domain(role)
    
    if not domain:
        domain = '[UNMATCHED]'
        unmatched_count += 1
    else:
        match_count += 1
        
    # Clean up names for the terminal printout
    company_name = title.split('[')[0].strip()
    short_role = (role[:32] + '...') if len(role) > 32 else role
    
    print(f"{company_name:<25} | {short_role:<35} | {domain}")

print("-" * 80)
print(f"TOTAL MATCHED: {match_count}")
print(f"TOTAL UNMATCHED: {unmatched_count}")
print("--- TEST COMPLETE ---\n")
