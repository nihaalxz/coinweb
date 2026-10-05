from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'merchant', 'category', 'price', 'original_price', 'discount_percent', 'coins_earned', 'is_featured', 'is_active')
    list_filter = ('merchant', 'category', 'is_active', 'is_featured', 'is_deal_of_the_day')
    search_fields = ('name', 'external_id', 'slug')
    prepopulated_fields = {'slug': ('name',)}
