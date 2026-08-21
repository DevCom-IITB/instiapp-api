import re
import dateparser
from bs4 import BeautifulSoup
from slugify import slugify
import json
from placementblogs.models import PlacementCompanyThread, PlacementBlogPost, PlacementExtractedData
from django.utils import timezone

POST_TYPE_MAP = {
    'jaf open': 'JAF_OPEN',
    'jafs open': 'JAF_OPEN',       
    'jaf update': 'JAF_UPDATE',
    'jafs update': 'JAF_UPDATE',  
    'test shortlist': 'TEST_SHORTLIST',
    'test update': 'TEST_UPDATE',
    'test': 'TEST',
    'assignment shortlist': 'ASSIGNMENT_SHORTLIST',
    'assignment details': 'ASSIGNMENT_DETAILS',
    'mandatory form': 'MANDATORY_FORM',
    'interview shortlist': 'INTERVIEW_SHORTLIST',
    'interview schedule': 'INTERVIEW_SCHEDULE',
    'interview update': 'INTERVIEW_UPDATE',
    'interview date': 'INTERVIEW_SCHEDULE', 
    'interview': 'INTERVIEW_SCHEDULE',      
    'gd schedule': 'GD_SCHEDULE',
    'gd update': 'GD_UPDATE',
    'round 2 shortlist': 'ROUND2_SHORTLIST',
    'final selection': 'FINAL_SELECTION',
    'selection': 'FINAL_SELECTION'
}

# Pre-compilation of regex patterns of the fields we need
PATTERNS = {
    # Catches: "Job code 1: Developer", "Job Code 2 - Analyst", "Job Code 3: PGTE - Controls"
    'role': re.compile(r'Job\s*[Cc]ode\s*\d*\s*[:\-–]\s*(.+)', re.IGNORECASE),
    
    # Catches: "CPI Cut-off: None", "CGPA Cutoff: 8.0"
    'cpi_cutoff': re.compile(r'(?:CPI|CGPA)\s*[Cc]ut-?[Oo]ff\s*[:\-]?\s*(.+)', re.IGNORECASE),
    
    # Catches: "Bonus JAF: Not Allowed", "Allow bonus applications: Yes"
    'bonus_jaf': re.compile(r'(?:Bonus\s*JAF|Allow\s*bonus\s*applications?)\s*[:\-]?\s*(.+)', re.IGNORECASE),
    
    # Catches: "Bond applicable: Yes", "Bond: No"
    'bond': re.compile(r'Bond(?: applicable)?\s*[:\-]?\s*(.+)', re.IGNORECASE),
    
    # Catches: "Deadline: 11:59 PM, 14th Feb"
    'deadline': re.compile(r'Deadline\s*[:\-]?\s*(.+)', re.IGNORECASE),

    # Catches: "Date: 15th December 2025"
    'event_date': re.compile(r'Date\s*[:\-]?\s*(.+)', re.IGNORECASE),
    
    # Catches: "Time: 9:00 PM", "Timeline: 10:00 AM", "Time Window: 3 PM - 4 PM"
    'time': re.compile(r'(?:Time|Reporting Time|Time Window|Timeline)\s*[:\-]?\s*(.+)', re.IGNORECASE),
    
    # Catches: "Venue: Placement Office"
    'venue': re.compile(r'Venue\s*[:\-]?\s*(.+)', re.IGNORECASE),
    
    # Catches: "Mode: Online from Hostel", "Mode: Pen & Paper"
    'mode': re.compile(r'Mode\s*[:\-]?\s*(.+)', re.IGNORECASE),

    # Catches both standard B.Tech (22B1234, 24M1234) AND 9-digit M.Tech/PhD (210040015)
    'roll_number': re.compile(r'^(\d{2}[A-Z]\d{4}|\d{9})$', re.IGNORECASE)
}

# To extract clean text from html_content provided
def get_text(html_content: str) -> str:
    # Force newlines for paragraph endings and line breaks BEFORE parsing
    html_content = html_content.replace('<br>', '\n').replace('<br />', '\n').replace('</p>', '\n</p>')
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract text using spaces to prevent inline tags from breaking
    text = soup.get_text(separator=' ')
    text = text.replace('\u200c', '').replace('\u200b', '')
    
    # Clean up extra spaces but preserve our real newlines
    lines = [re.sub(r' {2,}', ' ', line).strip() for line in text.split('\n')]
    return '\n'.join(line for line in lines if line)

# Helper function to just extract the string using the regex pattern
def extract_string(pattern, text: str) -> str:
    match = pattern.search(text)
    return match.group(1).strip() if match else ''

# Helper function to cleanly extract date and parse it 
def extract_date(pattern, text: str):
    date = extract_string(pattern, text)
    if date:
        parsed_date = dateparser.parse(date)
        # If the date is naive, force it to be timezone-aware
        if parsed_date and timezone.is_naive(parsed_date):
            return timezone.make_aware(parsed_date)
        return parsed_date
    return None

# To actually extract the fields 
def extract_fields(html_content: str) -> dict:
    text = get_text(html_content)

    # For roles we want all roles given so handled separately
    roles = PATTERNS['role'].findall(text)
    role_str = ', '.join(r.strip() for r in roles)

    return {
        "role": role_str,
        "raw_roles_list": roles,
        "cpi_cutoff": extract_string(PATTERNS['cpi_cutoff'], text), 
        "bonus_jaf": extract_string(PATTERNS['bonus_jaf'], text),   
        "bond": extract_string(PATTERNS['bond'], text),              
        "deadline": extract_date(PATTERNS['deadline'], text),
        "event_date": extract_date(PATTERNS['event_date'], text),
        "venue": extract_string(PATTERNS['venue'], text),
        "mode": extract_string(PATTERNS['mode'], text),              
        "time": extract_string(PATTERNS['time'], text)               
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

def extract_company_info(title: str):
    if '|' in title:
        parts = title.split('|', 1) # Split only on the first pipe
        company_name = parts[0].strip()
        keyword = parts[1].strip().lower()
    else:
        company_name = title.strip()
        keyword = ""
    return company_name, keyword

def extract_post_type(keyword: str) -> str:
    if not keyword:
        return 'OTHER'
    
    # Check for substring matches in our dictionary
    for key, value in POST_TYPE_MAP.items():
        if key in keyword:
            return value
            
    return 'OTHER'

def run_production_ingestion(feed_posts):
    for post in feed_posts:
        title = post.get('title', 'Unknown Title')
        content = post.get('content', '')
        link = post.get('link', '') 
        post_id = post.get('id')
        
        pub_date_str = post.get('published') or post.get('date_published')
        published_date = dateparser.parse(pub_date_str) if pub_date_str else timezone.now()
        
        if published_date and timezone.is_naive(published_date):
            published_date = timezone.make_aware(published_date)

        # 1. Parse the title using the new pipe logic
        clean_company_name, keyword = extract_company_info(title)
        post_type = extract_post_type(keyword)
        comp_slug = slugify(clean_company_name)

        # 2. Get or create the parent Company Thread FIRST
        thread, thread_created = PlacementCompanyThread.objects.get_or_create(
            company_slug=comp_slug,
            defaults={
                'company_name': clean_company_name,
                'first_post_date': published_date,
            }
        )

        # 3. Create the Post and link it to the Thread
        blog_post, created = PlacementBlogPost.objects.update_or_create(
            id=post_id,
            defaults={
                'thread': thread,         
                'post_type': post_type,
                'raw_company_name': title,
                'published': published_date,
                'raw_content': content,
                'link': link
            }
        )