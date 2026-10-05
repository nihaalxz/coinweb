import re
import json
from decimal import Decimal
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

def extract_product_metadata(url: str):
    """
    Extracts authentic product title, image, and details from Amazon, Flipkart, or Meesho URLs.
    Uses OpenGraph, Schema.org JSON-LD, and specific meta tags.
    """
    clean_url = url.strip()
    if not (clean_url.startswith('http://') or clean_url.startswith('https://')):
        clean_url = 'https://' + clean_url

    parsed = urlparse(clean_url)
    domain = parsed.netloc.lower()

    data = {
        'url': clean_url,
        'title': '',
        'image_url': '',
        'price': None,
        'original_price': None,
        'rating': 4.5,
        'store': 'Unknown',
        'store_slug': 'other',
    }

    if 'amazon.' in domain:
        data['store'] = 'Amazon India'
        data['store_slug'] = 'amazon-india'
    elif 'flipkart.' in domain:
        data['store'] = 'Flipkart'
        data['store_slug'] = 'flipkart'
    elif 'meesho.' in domain:
        data['store'] = 'Meesho'
        data['store_slug'] = 'meesho'
    elif 'myntra.' in domain:
        data['store'] = 'Myntra'
        data['store_slug'] = 'myntra'

    try:
        resp = requests.get(clean_url, headers=HEADERS, timeout=8)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')

            # 1. Title
            og_title = soup.find('meta', property='og:title') or soup.find('meta', attrs={'name': 'title'})
            if og_title and og_title.get('content'):
                data['title'] = og_title['content'].strip()
            elif soup.title and soup.title.string:
                raw_title = soup.title.string.strip()
                # Clean Amazon / Flipkart site suffixes
                cleaned = re.sub(r'(\s*:\s*Amazon\.in.*|\s*\|\s*Flipkart\.com.*|\s*Buy\s+at\s+Meesho.*)', '', raw_title, flags=re.I)
                data['title'] = cleaned.strip()

            # 2. Image
            og_image = soup.find('meta', property='og:image') or soup.find('link', rel='image_src')
            if og_image:
                img_url = og_image.get('content') or og_image.get('href')
                if img_url and img_url.startswith('http'):
                    data['image_url'] = img_url.strip()

            # 3. JSON-LD Schema
            scripts = soup.find_all('script', type='application/ld+json')
            for s in scripts:
                try:
                    if not s.string:
                        continue
                    schema = json.loads(s.string.strip())
                    if isinstance(schema, list):
                        schema = schema[0]
                    if isinstance(schema, dict):
                        if not data['title'] and schema.get('name'):
                            data['title'] = schema.get('name')
                        if not data['image_url'] and schema.get('image'):
                            img = schema.get('image')
                            if isinstance(img, list) and img:
                                data['image_url'] = img[0]
                            elif isinstance(img, str):
                                data['image_url'] = img
                        # Offers / Price
                        offers = schema.get('offers')
                        if isinstance(offers, dict) and offers.get('price'):
                            try:
                                data['price'] = Decimal(str(offers['price']))
                            except Exception:
                                pass
                        # Aggregate Rating
                        rating_obj = schema.get('aggregateRating')
                        if isinstance(rating_obj, dict) and rating_obj.get('ratingValue'):
                            try:
                                data['rating'] = float(rating_obj['ratingValue'])
                            except Exception:
                                pass
                except Exception:
                    continue
    except Exception as e:
        print(f"Scraper notice for {clean_url}: {e}")

    return data
