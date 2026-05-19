import re
import dateparser
from bs4 import BeautifulSoup
import json

# Pre-compilation of regex patterns of the fields we need
PATTERNS = {
    'category': re.compile(r'Category\s*:\s*([A-Z][0-9])', re.IGNORECASE),
    'role': re.compile(r'Profile\s*\d*\s*:\s*(.+)', re.IGNORECASE),
    'stipend': re.compile(r'Stipend\s*:\s*([\d,]+\s*(?:INR|USD|JPY|EUR)[^\n]*)', re.IGNORECASE),
    'eligibility': re.compile(r'Open\s*[Ff]or\s*:\s*(.+)', re.IGNORECASE),
    'deadline': re.compile(r'Deadline\s*:\s*(.+)', re.IGNORECASE),
    'event_date': re.compile(r'Date\s*:\s*(.+)', re.IGNORECASE),
    'venue': re.compile(r'Venue\s*:\s*(.+)', re.IGNORECASE),
    'reporting_time': re.compile(r'Reporting\s*Time\s*:\s*(.+)', re.IGNORECASE),
    'roll_number': re.compile(r'^\d{2}[A-Z]\d{4}$', re.IGNORECASE)
}

# To extract clean text from html_content provided
def get_text(html_content: str) -> str:
    text = BeautifulSoup(html_content, 'html.parser').get_text(separator='\n')
    # Strip zero-width non-joiners and zero-width spaces
    return text.replace('\u200c', '').replace('\u200b', '').strip()

# Helper function to just extract the string using the regex pattern
def extract_string(pattern, text: str) -> str:
    match = pattern.search(text)
    return match.group(1).strip() if match else ''

# Helper function to cleanly extract date and parse it 
def extract_date(pattern, text: str):
    date = extract_string(pattern, text)
    return dateparser.parse(date) if date else None

# To actually extract the fields 
def extract_fields(html_content: str) -> dict:
    text = get_text(html_content)

    # For roles we want all roles given so handled separately
    roles = PATTERNS['role'].findall(text)
    role_str = ', '.join(r.strip() for r in roles)

    return {
        "category": extract_string(PATTERNS['category'], text).upper(),
        "role": role_str,
        "stipend": extract_string(PATTERNS['stipend'], text),
        "eligibility": extract_string(PATTERNS['eligibility'], text),
        "deadline": extract_date(PATTERNS['deadline'], text),
        "event_date": extract_date(PATTERNS['event_date'], text),
        "venue": extract_string(PATTERNS['venue'], text),
        "reporting_time": extract_string(PATTERNS['reporting_time'], text)
    }

# To extract the roll numbers of the students 
def extract_roll_numbers(html_content: str) -> list:
    text = get_text(html_content)
    rolls = []

    for line in text.splitlines():
        parts = [p.strip() for p in line.split('|') if p.strip()]
        if not parts:
            continue

        candidate = parts[0].upper().strip()
        # Roll number format: 2-digit year + letter + 4 digits
        # Examples: 23B2241, 24B1247, 25N0191, 25M2221
        if PATTERNS['roll_number'].match(candidate):
            rolls.append(candidate)

    return rolls

# To extract the slots of the interviews of shortlisted students
def extract_interview_slots(html_content: str) -> list:
    text = get_text(html_content)
    slots = []

    for line in text.splitlines():
        parts = [p.strip() for p in line.split('|') if p.strip()]

        if len(parts) >= 4:
            roll = parts[0].upper().strip()
            if PATTERNS['roll_number'].match(roll):
                slots.append({
                    'roll': roll,
                    'name': parts[1],
                    'date': parts[2],
                    'time': parts[3], 
                })

    return slots



# For Testing the functions defined
if __name__ == "__main__":
    file_path = 'internship_blog_last500.json'

    with open(file_path, 'r', encoding='utf-8') as f:
        feed_data = json.load(f)

    posts = feed_data if isinstance(feed_data, list) else feed_data.get('items', [])
        
    print(f"Successfully loaded {len(posts)} posts. Testing the first 10...\n")
    print("-" * 60)

    for i, post in enumerate(posts[:10]):
        title = post.get('title', 'Unknown Title')
        content = post.get('content', '')
        
        print(f"[{i+1}] TITLE: {title}")

        if '[IAF OPEN]' in title.upper():
            data = extract_fields(content)
            print("    [Extracted IAF Data]:")
            print(json.dumps(data, indent=4, default=str))
            
        elif 'SCHEDULE' in title.upper():
            slots = extract_interview_slots(content)
            print(f"    [Interview Slots Found]: {len(slots)}")
            print("    [Sample Slots]:")
            print(json.dumps(slots[:2], indent=4))
            

        elif 'SHORTLIST' in title.upper():
            rolls = extract_roll_numbers(content)
            print(f"    [Rolls Found]: {len(rolls)}")
            print(f"    [Sample Rolls]: {rolls[:]}")
                
        else:
            print("    [Status]: Other post type. Skipping.")