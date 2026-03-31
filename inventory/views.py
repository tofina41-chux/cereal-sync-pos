from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Sale
from django.db.models import Q, Sum
from django.utils import timezone
from decimal import Decimal

def sales_dashboard(request):
    query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    
    products = Product.objects.all()
    categories = Category.objects.all()

    if query:
        products = products.filter(Q(name__icontains=query))
    
    if category_id:
        products = products.filter(category_id=category_id)

    # --- NEW: Daily Stats Logic ---
    today = timezone.now().date()
    daily_sales = Sale.objects.filter(created_at__date=today)
    
    # Calculate revenue and transaction count
    total_revenue = daily_sales.aggregate(Sum('total_price'))['total_price__sum'] or 0
    sales_count = daily_sales.count()

    # Find the top selling product today
    top_product_data = daily_sales.values('product__name').annotate(
        total_qty=Sum('quantity_sold')
    ).order_by('-total_qty').first()
    
    top_product = top_product_data['product__name'] if top_product_data else "None"

    # --- Cart Logic ---
    cart = request.session.get('cart', {})
    total_cart_value = sum(float(item.get('subtotal', 0)) for item in cart.values())

    return render(request, 'inventory/dashboard.html', {
        'products': products,
        'categories': categories,
        'query': query,
        'total_cart_value': total_cart_value,
        'total_revenue': total_revenue,
        'sales_count': sales_count,
        'top_product': top_product,
    })

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    quantity_raw = request.POST.get('quantity')
    try:
        quantity = float(quantity_raw) if quantity_raw and float(quantity_raw) > 0 else 1.0
    except ValueError:
        quantity = 1.0
    
    cart = request.session.get('cart', {})
    item_id = str(product_id)
    price = float(product.selling_price)
    
    if item_id in cart:
        cart[item_id]['quantity'] += quantity
        cart[item_id]['subtotal'] = cart[item_id]['quantity'] * price
    else:
        cart[item_id] = {
            'name': product.name,
            'price': price,
            'quantity': quantity,
            'subtotal': price * quantity,
        }
    
    request.session['cart'] = cart
    request.session.modified = True 
    return redirect('dashboard')

def clear_cart(request):
    if 'cart' in request.session:
        del request.session['cart']
    return redirect('dashboard')

def checkout(request):
    cart = request.session.get('cart', {})
    
    if not cart:
        return redirect('dashboard')

    try:
        for item_id, item in cart.items():
            product = get_object_or_404(Product, id=item_id)
            
            qty = Decimal(str(item['quantity']))
            price = Decimal(str(item['price']))
            total = qty * price

            Sale.objects.create(
                product=product,
                quantity_sold=qty,
                total_price=total
            )
        
        request.session['cart'] = {}
        request.session.modified = True
        
        return render(request, 'inventory/success.html')

    except Exception as e:
        print(f"Checkout Error: {e}")
        return redirect('dashboard')