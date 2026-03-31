from django.contrib import admin
from .models import Category, Product, Sale

# Keep only Category here
admin.site.register(Category)

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity_sold', 'total_price', 'created_at')
    list_filter = ('created_at', 'product')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'weight_in_stock', 'selling_price', 'low_stock_status')
    list_filter = ('category',)
    search_fields = ('name',)

    def low_stock_status(self, obj):
        # This handles the Red/Green logic you want
        return obj.weight_in_stock > obj.min_stock_level
    
    low_stock_status.boolean = True
    low_stock_status.short_description = 'In Stock'