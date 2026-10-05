import uuid
from decimal import Decimal
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from accounts.permissions import IsAdminRole, IsMarketingAdmin
from core.pagination import StandardResultsSetPagination
from audit.services import log_admin_action
from affiliate.models import AffiliateClick
from .models import Product
from .serializers import (
    ProductPublicSerializer,
    ProductAdminSerializer,
)
from .serpapi_service import search_live_products

class ProductPublicListView(generics.ListAPIView):
    """
    Public API: Browse products with filtering by merchant (Amazon, Flipkart, Meesho, etc.),
    category, featured status, search, and sorting by coins earned or price.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductPublicSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related('merchant')
        
        merchant = self.request.query_params.get('merchant', '').strip()
        category = self.request.query_params.get('category', '').strip()
        search = self.request.query_params.get('search', '').strip()
        featured = self.request.query_params.get('featured', '').strip()
        deal_of_day = self.request.query_params.get('deal_of_the_day', '').strip()
        min_price = self.request.query_params.get('min_price', '').strip()
        max_price = self.request.query_params.get('max_price', '').strip()
        sort = self.request.query_params.get('sort', '').strip()

        if merchant and merchant != 'all':
            qs = qs.filter(merchant__slug=merchant)
        if category and category != 'all':
            qs = qs.filter(category=category)
        if featured in ['true', '1']:
            qs = qs.filter(is_featured=True)
        if deal_of_day in ['true', '1']:
            qs = qs.filter(is_deal_of_the_day=True)
        if min_price:
            try:
                qs = qs.filter(price__gte=Decimal(min_price))
            except Exception:
                pass
        if max_price:
            try:
                qs = qs.filter(price__lte=Decimal(max_price))
            except Exception:
                pass

        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(category__icontains=search) |
                Q(merchant__name__icontains=search) |
                Q(deal_badge__icontains=search)
            )

        # Sorting
        if sort == 'price_asc':
            qs = qs.order_by('price')
        elif sort == 'price_desc':
            qs = qs.order_by('-price')
        elif sort == 'discount_desc':
            qs = qs.order_by('-discount_percent')
        elif sort == 'rating':
            qs = qs.order_by('-rating', '-review_count')
        else:
            # Default: Featured & display order
            qs = qs.order_by('display_order', '-is_featured', '-discount_percent', '-created_at')

        return qs

class ProductPublicDetailView(generics.RetrieveAPIView):
    """
    Public API: Product detail view.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductPublicSerializer
    queryset = Product.objects.filter(is_active=True).select_related('merchant')
    lookup_field = 'id'

class ProductClickTrackView(APIView):
    """
    CashKaro style tracked click endpoint.
    User clicks 'Buy & Earn Coins' on a product:
    - Generates unique click_id
    - Attaches sub-id and affiliate network tracking tags to the product URL
    - Records AffiliateClick in database
    - Returns redirect_url with estimated coins
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, id):
        product = get_object_or_404(Product, id=id, is_active=True)
        click_id = uuid.uuid4()
        user = request.user if request.user.is_authenticated else None
        user_id_str = str(user.id) if user else "guest"

        source = request.data.get('source', 'web_deal_card')
        campaign = request.data.get('campaign', 'product_showcase')
        sub_id = request.data.get('sub_id', user_id_str)

        # Build full tracked affiliate redirect URL for this product
        redirect_url = product.build_affiliate_url(click_id=str(click_id), user_id=user_id_str)

        # Extract client IP and user agent
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip_addr = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        click = AffiliateClick.objects.create(
            click_id=click_id,
            user=user,
            merchant=product.merchant,
            source=source,
            campaign=campaign,
            sub_id=sub_id,
            product_title=product.name,
            product_url=product.target_url,
            estimated_coins=product.coins_earned,
            ip_address=ip_addr,
            user_agent=user_agent[:500] if user_agent else "",
            redirect_url=redirect_url
        )

        return Response({
            'success': True,
            'click_id': str(click.click_id),
            'product_name': product.name,
            'merchant_name': product.merchant.name,
            'merchant_slug': product.merchant.slug,
            'price': str(product.price),
            'coins_earned': product.coins_earned,
            'coin_reward_rate': str(product.effective_reward_rate),
            'redirect_url': click.redirect_url,
        }, status=status.HTTP_201_CREATED)

class AdminProductListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = ProductAdminSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = Product.objects.all().select_related('merchant')
        merchant_id = self.request.query_params.get('merchant_id', '').strip()
        search = self.request.query_params.get('search', '').strip()

        if merchant_id:
            qs = qs.filter(merchant_id=merchant_id)
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(external_id__icontains=search))

        return qs.order_by('display_order', '-created_at')

    def perform_create(self, serializer):
        product = serializer.save()
        log_admin_action(
            admin_user=self.request.user,
            action='PRODUCT_CREATED',
            entity='Product',
            entity_id=str(product.id),
            new_values={'name': product.name, 'merchant': product.merchant.name, 'price': str(product.price)},
            reason="Added new product deal.",
            request=self.request
        )

class AdminProductDetailUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsMarketingAdmin]
    serializer_class = ProductAdminSerializer
    queryset = Product.objects.all().select_related('merchant')


class LiveProductSearchView(APIView):
    """
    Fetches LIVE products from SerpAPI Google Shopping in real-time.
    This powers the Product Deals Showcase on the frontend with actual
    Amazon India, Flipkart, and Meesho listings.

    Query params:
      - merchant:  'amazon-india' | 'flipkart' | 'meesho' | 'myntra' | 'all'
      - category:  'mobiles' | 'electronics' | 'fashion' | 'home_kitchen' | 'beauty' | 'appliances' | 'all'
      - search:    free-text product search
      - page:      page number (default 1)
      - page_size: results per page (default 20, max 40)
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        merchant = request.query_params.get('merchant', 'all').strip()
        category = request.query_params.get('category', 'all').strip()
        search = request.query_params.get('search', '').strip()
        sort = request.query_params.get('sort', '').strip()

        try:
            page = max(1, int(request.query_params.get('page', 1)))
        except (ValueError, TypeError):
            page = 1

        try:
            page_size = min(40, max(4, int(request.query_params.get('page_size', 20))))
        except (ValueError, TypeError):
            page_size = 20

        result = search_live_products(
            merchant_slug=merchant,
            category=category,
            search_query=search,
            page=page,
            page_size=page_size,
        )

        # Client-side sort (SerpAPI doesn't support our sort options natively)
        items = result.get('results', [])
        if sort == 'price_asc':
            items = sorted(items, key=lambda x: float(x.get('price', 0) or 0))
        elif sort == 'price_desc':
            items = sorted(items, key=lambda x: float(x.get('price', 0) or 0), reverse=True)
        elif sort == 'discount_desc':
            items = sorted(items, key=lambda x: int(x.get('discount_percent', 0) or 0), reverse=True)
        elif sort == 'coins_desc':
            items = sorted(items, key=lambda x: int(x.get('coins_earned', 0) or 0), reverse=True)

        return Response({
            'results': items,
            'count': result.get('count', len(items)),
            'next': result.get('next', False),
            'source': result.get('source', 'serpapi'),
            'error': result.get('error'),
        })
