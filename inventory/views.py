from django.shortcuts import render, redirect
from .models import Product, Category, Sale
from django.db.models import Q

def sales_dashboard(request):
    query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    
    products = Product.objects.all()
    categories = Category.objects.all()

    # Apply Search Logic
    if query:
        products = products.filter(Q(name__icontains=query))
    
    # Apply Category Logic
    if category_id:
        products = products.filter(category_id=category_id)

    return render(request, 'inventory/dashboard.html', {
        'products': products,
        'categories': categories,
        'query': query,
    })