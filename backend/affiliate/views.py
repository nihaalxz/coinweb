import uuid
from urllib.parse import urlencode, urlparse, parse_qsl, urlunparse
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from accounts.permissions import IsAdminRole
from core.pagination import StandardResultsSetPagination
from merchants.models import Merchant
from .models import AffiliateClick
from .serializers import AffiliateClickSerializer

class CreateClickAndRedirectView(APIView):
    """
    Public / Authenticated endpoint to track affiliate click and resolve destination.
    Accepts merchant_slug and optional source/campaign parameters.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, merchant_slug):
        merchant = get_object_or_404(Merchant, slug=merchant_slug, is_active=True)
        click_id = uuid.uuid4()
        user = request.user if request.user.is_authenticated else None
        user_id_str = str(user.id) if user else "guest"

        source = request.data.get('source', 'web')
        campaign = request.data.get('campaign', '')
        sub_id = request.data.get('sub_id', '')

        # Resolve destination affiliate URL
        template = merchant.affiliate_url_template.strip()
        if template:
            redirect_url = template.replace('{click_id}', str(click_id))\
                                   .replace('{user_id}', user_id_str)\
                                   .replace('{merchant_slug}', merchant.slug)
        else:
            # Fallback: append tracking params to website_url
            parsed = urlparse(merchant.website_url)
            query = dict(parse_qsl(parsed.query))
            query['cbk_click'] = str(click_id)
            query['cbk_sub'] = user_id_str
            parts = list(parsed)
            parts[4] = urlencode(query)
            redirect_url = urlunparse(parts)

        # Extract client IP and user agent
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip_addr = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        click = AffiliateClick.objects.create(
            click_id=click_id,
            user=user,
            merchant=merchant,
            source=source,
            campaign=campaign,
            sub_id=sub_id,
            ip_address=ip_addr,
            user_agent=user_agent[:500] if user_agent else "",
            redirect_url=redirect_url
        )

        return Response({
            'click_id': str(click.click_id),
            'merchant_name': merchant.name,
            'redirect_url': click.redirect_url,
        }, status=status.HTTP_201_CREATED)

class AdminAffiliateClickListView(generics.ListAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = AffiliateClickSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = AffiliateClick.objects.all().select_related('merchant', 'user')
        search = self.request.query_params.get('search', '').strip()
        merchant_id = self.request.query_params.get('merchant_id', '').strip()
        status_val = self.request.query_params.get('status', '').strip()

        if search:
            qs = qs.filter(
                Q(click_id__icontains=search) |
                Q(merchant__name__icontains=search) |
                Q(user__email__icontains=search)
            )
        if merchant_id:
            qs = qs.filter(merchant_id=merchant_id)
        if status_val:
            qs = qs.filter(status=status_val)

        return qs.order_by('-created_at')

class AdminAffiliateClickDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = AffiliateClickSerializer
    lookup_field = 'click_id'
    queryset = AffiliateClick.objects.all().select_related('merchant', 'user')

class ConvertLinkView(APIView):
    """
    CashKaro style 'Make Profit Link' / 'Convert Any Link' API.
    Users can paste any product URL from Amazon, Flipkart, Meesho, Myntra, etc.
    1. Detects store merchant automatically
    2. Builds tracked affiliate URL
    3. Generates click_id and records click
    4. Calculates estimated coins earned per ₹1,000
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        input_url = request.data.get('url', '').strip()
        if not input_url:
            return Response({'error': 'Please provide a valid product URL.'}, status=status.HTTP_400_BAD_REQUEST)

        # Basic URL normalization
        if not (input_url.startswith('http://') or input_url.startswith('https://')):
            input_url = 'https://' + input_url

        try:
            parsed = urlparse(input_url)
            netloc = parsed.netloc.lower()
        except Exception:
            return Response({'error': 'Invalid URL format.'}, status=status.HTTP_400_BAD_REQUEST)

        merchant = None
        if 'amazon.' in netloc or 'amzn.' in netloc:
            merchant = Merchant.objects.filter(slug='amazon-india', is_active=True).first()
        elif 'flipkart.' in netloc or 'fkrt.' in netloc:
            merchant = Merchant.objects.filter(slug='flipkart', is_active=True).first()
        elif 'meesho.' in netloc:
            merchant = Merchant.objects.filter(slug='meesho', is_active=True).first()
        elif 'myntra.' in netloc:
            merchant = Merchant.objects.filter(slug='myntra', is_active=True).first()
        elif 'ajio.' in netloc:
            merchant = Merchant.objects.filter(slug='ajio', is_active=True).first()
        elif 'nykaa.' in netloc:
            merchant = Merchant.objects.filter(slug='nykaa', is_active=True).first()
        elif 'croma.' in netloc:
            merchant = Merchant.objects.filter(slug='croma', is_active=True).first()
        elif 'makemytrip.' in netloc:
            merchant = Merchant.objects.filter(slug='makemytrip', is_active=True).first()

        # Fallback check against website_url in all active merchants
        if not merchant:
            for m in Merchant.objects.filter(is_active=True):
                m_netloc = urlparse(m.website_url).netloc.lower()
                if m_netloc and (m_netloc in netloc or netloc in m_netloc):
                    merchant = m
                    break

        if not merchant:
            return Response({
                'error': 'Unsupported store. We currently support Amazon India, Flipkart, Meesho, Myntra, AJIO, Nykaa, and Croma.'
            }, status=status.HTTP_404_NOT_FOUND)

        click_id = uuid.uuid4()
        user = request.user if request.user.is_authenticated else None
        user_id_str = str(user.id) if user else "guest"

        query = dict(parse_qsl(parsed.query))
        if 'amazon.' in netloc or merchant.slug == 'amazon-india':
            query['tag'] = 'coinweb-21'
            query['ascsubtag'] = str(click_id)
            query['linkCode'] = 'll1'
        elif 'flipkart.' in netloc or merchant.slug == 'flipkart':
            query['affid'] = 'coinweb'
            query['affExtParam1'] = str(click_id)
            query['affExtParam2'] = user_id_str
        elif 'meesho.' in netloc or merchant.slug == 'meesho':
            query['cbk_click'] = str(click_id)
            query['cbk_sub'] = user_id_str
            query['utm_source'] = 'coinweb'
            query['utm_campaign'] = 'link_converter'
        else:
            query['cbk_click'] = str(click_id)
            query['cbk_sub'] = user_id_str

        parts = list(parsed)
        parts[4] = urlencode(query)
        redirect_url = urlunparse(parts)

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip_addr = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        custom_title = request.data.get('product_title', '').strip()
        custom_image = request.data.get('product_image', '').strip()
        live_price = None

        # Try live metadata extraction from Amazon, Flipkart, Meesho
        try:
            from products.scraper import extract_product_metadata
            meta = extract_product_metadata(input_url)
            if not custom_title and meta.get('title'):
                custom_title = meta['title']
            if not custom_image and meta.get('image_url'):
                custom_image = meta['image_url']
            if meta.get('price'):
                live_price = meta['price']
        except Exception as e:
            pass

        if not custom_title:
            custom_title = f"{merchant.name} Product Link"

        click = AffiliateClick.objects.create(
            click_id=click_id,
            user=user,
            merchant=merchant,
            source='link_converter',
            campaign='user_custom_url',
            sub_id=user_id_str,
            product_title=custom_title,
            product_url=input_url,
            ip_address=ip_addr,
            user_agent=user_agent[:500] if user_agent else "",
            redirect_url=redirect_url
        )

        coins_per_1000 = int(round((1000.0 * float(merchant.cbk_reward_rate)) / 100.0))

        return Response({
            'success': True,
            'click_id': str(click.click_id),
            'merchant': {
                'id': merchant.id,
                'name': merchant.name,
                'slug': merchant.slug,
                'category': merchant.category,
                'reward_rate': str(merchant.cbk_reward_rate),
                'badge': merchant.reward_badge or 'VERIFIED',
            },
            'product_title': custom_title,
            'product_image': custom_image,
            'original_url': input_url,
            'redirect_url': redirect_url,
            'coins_per_1000': coins_per_1000,
            'message': f"Earn {merchant.cbk_reward_rate}% cashback coins on your purchase!"
        }, status=status.HTTP_201_CREATED)

