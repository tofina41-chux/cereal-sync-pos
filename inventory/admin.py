from django.contrib import admin
from .models import Category, Product

admin.site.register(Category)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Added 'low_stock_status' to the list
    list_display = ('name', 'category', 'weight_in_stock', 'selling_price', 'low_stock_status')
    list_filter = ('category',)
    search_fields = ('name',)

    # This function creates the Red/Green logic
    def low_stock_status(self, obj):
        if obj.weight_in_stock <= obj.min_stock_level:
            return False # Shows a Red icon in Django Admin
        return True # Shows a Green icon
    
    low_stock_status.boolean = True
    low_stock_status.short_description = 'In Stock'