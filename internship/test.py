import os
import sys
import django
import json

# 1. ADD ROOT DIRECTORY TO SYSTEM PATH
# This dynamically finds the root folder (instiapp-api) and tells Python to look there
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# 2. SETUP DJANGO ENVIRONMENT
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings') 
django.setup()

# 3. NOW IT IS SAFE TO IMPORT DJANGO LOGIC
from internship.data_extractor import run_production_ingestion

file_path = 'internship_blog_last500.json'

with open(file_path, 'r', encoding='utf-8') as f:
    feed_data = json.load(f)
    
posts = feed_data if isinstance(feed_data, list) else feed_data.get('items', [])

print(f"Starting database ingestion for {len(posts)} posts...")

# This will now successfully write to db.sqlite3
run_production_ingestion(posts)

print("Ingestion complete!")



from rest_framework.test import APIClient
from django.urls import reverse

# Initialize the test client
client = APIClient()

print("\n--- TESTING API VIEWS AGAINST LIVE DATABASE ---")

# 1. Test the List View
list_url = reverse('thread-list')
response = client.get(list_url)

print(f"List View Status: {response.status_code}")
if response.status_code == 200:
    print(f"Total Threads Fetched: {len(response.data)}")

# 2. Test the Detail View (Dynamically grabbing the first thread's slug)
if response.status_code == 200 and len(response.data) > 0:
    first_slug = response.data[0]['company_slug']
    first_company = response.data[0]['company_name']
    
    detail_url = reverse('thread-detail', kwargs={'company_slug': first_slug})
    detail_response = client.get(detail_url)
    
    print(f"\nDetail View Status for '{first_company}': {detail_response.status_code}")
    
    if detail_response.status_code == 200 and 'posts' in detail_response.data:
        post_count = len(detail_response.data['posts'])
        print(f"Total updates/posts fetched for this thread: {post_count}")