import re
import dateparser
from bs4 import BeautifulSoup
from slugify import slugify
import json
from internship.models import CompanyThread, BlogPost, ExtractedData
from django.utils import timezone

POST_TYPE_MAP = {
    'iaf open': 'IAF_OPEN',
    'test shortlist': 'TEST_SHORTLIST',
    'test update': 'TEST_UPDATE',
    'test': 'TEST',
    'assignment shortlist': 'ASSIGNMENT_SHORTLIST',
    'assignment details': 'ASSIGNMENT_DETAILS',
    'mandatory form': 'MANDATORY_FORM',
    'interview shortlist': 'INTERVIEW_SHORTLIST',
    'interview schedule': 'INTERVIEW_SCHEDULE',
    'interview update': 'INTERVIEW_UPDATE',
    'gd schedule': 'GD_SCHEDULE',
    'gd update': 'GD_UPDATE',
    'round 2 shortlist': 'ROUND2_SHORTLIST',
    'final selection': 'FINAL_SELECTION'
}

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

# to normalise the name of the company
def normalize_company_name(title: str) -> str:
    # Step 1: remove [Event Tag] at end
    name = re.sub(r'\s*\[.*?\]\s*$', '', title).strip()
    # Step 2: remove trailing (Variant) parenthetical only
    name = re.sub(r'\s*\([^)]*\)\s*$', '', name).strip()
    return name

# to create the company slug using normalised company name
def company_slug(title: str) -> str:
    return slugify(normalize_company_name(title))

# to extract type of the post based on post type map 
def extract_post_type(title: str) -> str:
    match = re.search(r'\[(.+?)\]', title)
    if not match:
        return 'OTHER'
    
    tag = match.group(1).strip().lower()
    # Check for substring matches to handle variants
    for key, value in POST_TYPE_MAP.items():
        if key in tag:
            return value
    return 'OTHER'




def run_database_ingestion():
    file_path = 'internship/internship_blog_last500.json'

    with open(file_path, 'r', encoding='utf-8') as f:
        feed_data = json.load(f)

    posts = feed_data if isinstance(feed_data, list) else feed_data.get('items', [])
        
    print(f"Successfully loaded {len(posts)} posts. Starting database ingestion...\n")

    for i, post in enumerate(posts):
        title = post.get('title', 'Unknown Title')
        content = post.get('content', '')
        link = post.get('link', '') 
        post_id = post.get('id')
        
        pub_date_str = post.get('published') or post.get('date_published')
        published_date = dateparser.parse(pub_date_str) if pub_date_str else timezone.now()

        post_type = extract_post_type(title)
        company_name = normalize_company_name(title)
        c_slug = company_slug(title)

        company_thread, created = CompanyThread.objects.get_or_create(
            company_name=company_name,
            defaults={
                'company_slug': c_slug,
                'first_post_date': published_date
            }
        )
        if created:
            print(f"[NEW THREAD] Created database thread for: {company_name}")

        blog_post = BlogPost.objects.create(
            id=post_id,
            thread=company_thread,
            post_type=post_type,
            raw_company_name=title,
            published=published_date,
            raw_content=content,
            link=link
        )

        ext_data = ExtractedData(post=blog_post)

        if post_type == 'IAF_OPEN':
            data = extract_fields(content)
            
            company_thread.category = data.get('category', '')
            company_thread.role = data.get('role', '')
            company_thread.stipend = data.get('stipend', '')
            company_thread.eligibility = data.get('eligibility', '')
            company_thread.iaf_deadline = data.get('deadline')
            company_thread.save()

            ext_data.category = data.get('category', '')
            ext_data.role = data.get('role', '')
            ext_data.stipend = data.get('stipend', '')
            ext_data.eligibility = data.get('eligibility', '')
            ext_data.deadline = data.get('deadline')
            ext_data.event_date = data.get('event_date')
            ext_data.venue = data.get('venue', '')
            ext_data.reporting_time = data.get('reporting_time', '')
            
            print(f"[SAVED] IAF Data extracted and saved for {company_name}")
            
        elif post_type in ['INTERVIEW_SCHEDULE', 'GD_SCHEDULE']:
            ext_data.interview_slots = extract_interview_slots(content)
            print(f"[LOG] Saved {len(ext_data.interview_slots)} interview slots for {company_name}")

        elif 'SHORTLIST' in post_type:
            ext_data.shortlisted_rolls = extract_roll_numbers(content)
            print(f"[LOG] Saved {len(ext_data.shortlisted_rolls)} shortlisted rolls for {company_name}")
                
        else:
            print(f"[SKIPPED] {company_name} - Post type is {post_type}")

        ext_data.save()

    print("\n Data ingestion complete! All models populated.")

run_database_ingestion()