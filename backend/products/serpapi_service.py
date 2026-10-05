"""
SerpAPI Product Search Service
================================
Fetches LIVE product listings from Google Shopping via SerpAPI.
Filters results to Amazon India, Flipkart, and Meesho.

The service normalises every result into a unified ProductResult dict
that mirrors the format returned by the DB Product model serializer,
so the frontend can consume both sources identically.

Docs: https://serpapi.com/google-shopping-api
"""

import math
import re
import hashlib
import logging
from decimal import Decimal, InvalidOperation
from typing import Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# ─── Merchant meta ────────────────────────────────────────────────────────────
MERCHANT_META = {
    'amazon': {
        'name': 'Amazon India',
        'slug': 'amazon-india',
        'reward_rate': Decimal('8.50'),
        'domain_keywords': ['amazon.in', 'amazon.com/dp'],
        'source_keywords': ['amazon'],
        'badge': 'AMAZON DEAL',
        'affiliate_tag': 'coinweb-21',
    },
    'flipkart': {
        'name': 'Flipkart',
        'slug': 'flipkart',
        'reward_rate': Decimal('12.00'),
        'domain_keywords': ['flipkart.com'],
        'source_keywords': ['flipkart'],
        'badge': 'FLIPKART DEAL',
        'affiliate_tag': 'coinweb',
    },
    'meesho': {
        'name': 'Meesho',
        'slug': 'meesho',
        'reward_rate': Decimal('15.00'),
        'domain_keywords': ['meesho.com'],
        'source_keywords': ['meesho'],
        'badge': 'MEESHO DEAL',
        'affiliate_tag': 'coinweb_ms',
    },
    'myntra': {
        'name': 'Myntra',
        'slug': 'myntra',
        'reward_rate': Decimal('9.50'),
        'domain_keywords': ['myntra.com'],
        'source_keywords': ['myntra'],
        'badge': 'MYNTRA DEAL',
        'affiliate_tag': 'coinweb_mn',
    },
}

SUPPORTED_SOURCES = list(MERCHANT_META.keys())

# Map category keywords used in SerpAPI → our category names
CATEGORY_KEYWORD_MAP = {
    'mobiles': ['mobile', 'smartphone', 'phone', 'iphone', 'android', 'samsung galaxy', 'oneplus', 'redmi', 'realme', 'vivo', 'oppo'],
    'electronics': ['laptop', 'headphone', 'earphone', 'speaker', 'smartwatch', 'watch', 'tablet', 'ipad', 'tv', 'television', 'camera', 'earbuds', 'audio', 'monitor', 'keyboard', 'mouse'],
    'fashion': ['shirt', 'kurta', 'saree', 'dress', 'jeans', 'shoes', 'sneaker', 'kurti', 'lehenga', 'top', 'suit', 'jacket', 'ethnic', 'anarkali', 'pant', 'trouser'],
    'home_kitchen': ['kitchen', 'cookware', 'bottle', 'container', 'bedsheet', 'pillow', 'towel', 'curtain', 'organizer', 'sofa', 'home decor', 'storage'],
    'beauty': ['cream', 'serum', 'shampoo', 'lotion', 'lipstick', 'foundation', 'moisturizer', 'sunscreen', 'perfume', 'hair care', 'skin care', 'makeup'],
    'appliances': ['washing machine', 'refrigerator', 'microwave', 'air conditioner', 'mixer', 'juicer', 'geyser', 'iron', 'vacuum', 'air fryer', 'cooler'],
}


def _detect_merchant(source: str, link: str = '') -> Optional[dict]:
    """Identify which supported merchant a result belongs to."""
    source_lower = source.lower() if source else ''
    link_lower = link.lower() if link else ''
    for key, meta in MERCHANT_META.items():
        for kw in meta['source_keywords']:
            if kw in source_lower:
                return meta
        for kw in meta['domain_keywords']:
            if kw in link_lower:
                return meta
    return None


def _detect_category(title: str) -> str:
    """Best-effort category detection from product title."""
    title_lower = title.lower()
    for category, keywords in CATEGORY_KEYWORD_MAP.items():
        for kw in keywords:
            if kw in title_lower:
                return category
    return 'other'


def _parse_price(raw) -> Optional[Decimal]:
    """Parse price from SerpAPI extracted price field (string or number)."""
    if raw is None:
        return None
    try:
        # Remove currency symbols and commas
        cleaned = re.sub(r'[₹$,\s]', '', str(raw))
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return None


def _calculate_coins(price: Decimal, reward_rate: Decimal) -> int:
    """Calculate coins earned: floor((price * rate) / 100), minimum 1."""
    try:
        coins = math.floor((float(price) * float(reward_rate)) / 100.0)
        return max(coins, 1)
    except Exception:
        return 1


def _build_affiliate_url(url: str, merchant_key: str, click_id: str = 'serpapi_live') -> str:
    """Append affiliate tracking parameters to a product URL."""
    meta = MERCHANT_META.get(merchant_key)
    if not meta:
        return url
    sep = '&' if '?' in url else '?'
    if merchant_key == 'amazon':
        return f"{url}{sep}tag={meta['affiliate_tag']}&ascsubtag={click_id}&linkCode=ll1"
    elif merchant_key == 'flipkart':
        return f"{url}{sep}affid=coinweb&affExtParam1={click_id}"
    elif merchant_key == 'meesho':
        return f"{url}{sep}cbk_click={click_id}&utm_source=coinweb_cashback&utm_campaign=serp_live"
    else:
        return f"{url}{sep}cbk_click={click_id}"


def _stable_id(link: str, title: str) -> int:
    """Generate a stable integer pseudo-ID from product URL + title (for frontend keying)."""
    raw = (link or '') + '|' + (title or '')
    return int(hashlib.md5(raw.encode()).hexdigest()[:8], 16)


def _normalise_result(item: dict, merchant_key: str) -> dict:
    """Convert a raw SerpAPI shopping result into our unified ProductResult format."""
    meta = MERCHANT_META[merchant_key]
    title = item.get('title', '')
    link = item.get('link', '') or item.get('product_link', '')
    image = item.get('thumbnail', '') or item.get('image', '')

    # Price handling
    price_raw = item.get('extracted_price') or item.get('price')
    old_price_raw = item.get('extracted_old_price') or item.get('old_price')

    price = _parse_price(price_raw)
    original_price = _parse_price(old_price_raw)

    # Fallback: if no original price, use price * 1.2 to show a small "discount"
    if price and not original_price:
        original_price = price  # no discount shown

    # Discount percent
    discount_percent = 0
    if price and original_price and original_price > price:
        discount_percent = int(round(((original_price - price) / original_price) * 100))

    # Rating
    rating_raw = item.get('rating') or item.get('reviews', {}).get('rating') if isinstance(item.get('reviews'), dict) else None
    try:
        rating = round(float(rating_raw), 1) if rating_raw else 4.2
    except (ValueError, TypeError):
        rating = 4.2
    rating = max(1.0, min(5.0, rating))

    # Review count
    reviews_raw = item.get('reviews') or item.get('reviews_count') or item.get('reviews_results', {}).get('reviews_count') if isinstance(item.get('reviews_results'), dict) else None
    try:
        if isinstance(reviews_raw, dict):
            review_count = int(reviews_raw.get('count', 100))
        elif isinstance(reviews_raw, int):
            review_count = reviews_raw
        else:
            review_count = int(str(reviews_raw).replace(',', '')) if reviews_raw else 100
    except (ValueError, TypeError):
        review_count = 100

    # Badge
    badge = meta['badge']
    if discount_percent >= 50:
        badge = f"{discount_percent}% OFF"
    elif discount_percent >= 30:
        badge = f"HOT DEAL {discount_percent}%"

    # Coins
    coins_earned = _calculate_coins(price, meta['reward_rate']) if price else 1

    # Category
    category = _detect_category(title)

    # Affiliate link
    pseudo_click_id = 'live_' + hashlib.md5(link.encode()).hexdigest()[:8]
    affiliate_url = _build_affiliate_url(link, merchant_key, pseudo_click_id)

    return {
        'id': _stable_id(link, title),
        'name': title,
        'slug': re.sub(r'[^a-z0-9]+', '-', title.lower())[:120].strip('-'),
        'external_id': item.get('product_id', ''),
        'merchant_name': meta['name'],
        'merchant_slug': meta['slug'],
        'category': category,
        'category_display': {
            'mobiles': 'Mobiles & Tablets',
            'electronics': 'Electronics & Gadgets',
            'fashion': 'Fashion & Apparel',
            'home_kitchen': 'Home & Kitchen',
            'beauty': 'Beauty & Personal Care',
            'appliances': 'Appliances',
            'other': 'Other',
        }.get(category, 'Other'),
        'image_url': image,
        'target_url': link,
        'affiliate_url': affiliate_url,
        'price': str(price) if price else '0',
        'original_price': str(original_price) if original_price else str(price) if price else '0',
        'discount_percent': discount_percent,
        'rating': str(rating),
        'review_count': review_count,
        'deal_badge': badge,
        'effective_reward_rate': str(meta['reward_rate']),
        'coins_earned': coins_earned,
        'is_featured': discount_percent >= 20 or item.get('badge') is not None,
        'is_deal_of_the_day': discount_percent >= 40,
        'source': 'serpapi_live',
    }


# ─── Query builder ────────────────────────────────────────────────────────────

MERCHANT_QUERY_MAP = {
    'amazon-india': ('amazon', 'site:amazon.in'),
    'flipkart': ('flipkart', 'site:flipkart.com'),
    'meesho': ('meesho', 'site:meesho.com'),
    'myntra': ('myntra', 'site:myntra.com'),
}

CATEGORY_QUERY_TERMS = {
    'mobiles': 'smartphones mobile phones',
    'electronics': 'electronics gadgets laptops headphones',
    'fashion': 'fashion clothing apparel',
    'home_kitchen': 'home kitchen products',
    'beauty': 'beauty personal care',
    'appliances': 'home appliances',
    'all': 'trending deals best sellers',
}


def search_live_products(
    merchant_slug: str = 'all',
    category: str = 'all',
    search_query: str = '',
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """
    Main entry point: fetches live products from SerpAPI Google Shopping.

    Returns a dict with:
      - results: list of normalised ProductResult dicts
      - count: total estimated result count
      - next: boolean (has more pages)
      - source: 'serpapi'
    """
    api_key = getattr(settings, 'SERPAPI_KEY', '')
    if not api_key:
        logger.warning("SERPAPI_KEY not configured. Returning empty results.")
        return {'results': [], 'count': 0, 'next': False, 'source': 'serpapi', 'error': 'SERPAPI_KEY not set'}

    # Build the search query
    if search_query:
        base_query = search_query
    else:
        cat_term = CATEGORY_QUERY_TERMS.get(category, CATEGORY_QUERY_TERMS['all'])
        base_query = cat_term

    # Merchant filter
    target_merchants: list[str] = []
    site_filter = ''

    if merchant_slug != 'all' and merchant_slug in MERCHANT_QUERY_MAP:
        merchant_key, site_q = MERCHANT_QUERY_MAP[merchant_slug]
        target_merchants = [merchant_key]
        site_filter = site_q
        query = f"{base_query} {site_filter}".strip()
    else:
        # All merchants: search without site filter but will filter results by merchant
        target_merchants = list(MERCHANT_META.keys())
        query = f"{base_query} india buy online".strip()

    # SerpAPI pagination: `start` param (0-indexed offset)
    start = (page - 1) * page_size

    params = {
        'engine': 'google_shopping',
        'q': query,
        'api_key': api_key,
        'gl': 'in',          # Country: India
        'hl': 'en',          # Language: English
        'num': min(page_size * 2, 100),  # Fetch extra to allow merchant filtering
        'start': start,
        'tbs': 'mr:1,avg_rating:400',  # Min 4 stars by default
    }

    logger.info(f"SerpAPI request: query={query!r}, merchant={merchant_slug}, page={page}")

    try:
        resp = requests.get(
            'https://serpapi.com/search',
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.Timeout:
        logger.error("SerpAPI request timed out")
        return {'results': [], 'count': 0, 'next': False, 'source': 'serpapi', 'error': 'timeout'}
    except requests.exceptions.RequestException as e:
        logger.error(f"SerpAPI request error: {e}")
        return {'results': [], 'count': 0, 'next': False, 'source': 'serpapi', 'error': str(e)}

    # Parse results
    shopping_results = data.get('shopping_results', [])
    if not shopping_results:
        # Try inline_shopping_results fallback
        shopping_results = data.get('inline_shopping_results', [])

    normalised = []
    seen_ids = set()

    for item in shopping_results:
        source = (item.get('source') or '').lower()
        link = item.get('link', '') or item.get('product_link', '')

        # Identify merchant
        merchant_meta = _detect_merchant(source, link)
        if not merchant_meta:
            continue

        # Check if this merchant is in our target list
        merchant_key = next(
            (k for k, v in MERCHANT_META.items() if v['slug'] == merchant_meta['slug']),
            None
        )
        if merchant_key not in target_merchants:
            continue

        # Skip if no price
        price_raw = item.get('extracted_price') or item.get('price')
        if not price_raw:
            continue

        result = _normalise_result(item, merchant_key)
        pid = result['id']
        if pid not in seen_ids:
            seen_ids.add(pid)
            normalised.append(result)

        if len(normalised) >= page_size:
            break

    # Estimate total
    total_estimate = data.get('search_information', {}).get('total_results', len(normalised))
    if isinstance(total_estimate, str):
        try:
            total_estimate = int(re.sub(r'[^0-9]', '', total_estimate))
        except ValueError:
            total_estimate = len(normalised)

    has_next = len(normalised) >= page_size and bool(data.get('serpapi_pagination', {}).get('next'))

    logger.info(f"SerpAPI returned {len(normalised)} results (raw: {len(shopping_results)})")

    return {
        'results': normalised,
        'count': min(total_estimate, 500),  # cap to reasonable number
        'next': has_next,
        'source': 'serpapi',
    }
