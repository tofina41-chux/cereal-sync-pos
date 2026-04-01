from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Sale
from django.db.models import Q, Sum
from django.utils import timezone
from decimal import Decimal
import uuid 
from .mpesa_utils import get_access_token, generate_mpesa_password
import requests
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def mpesa_callback(request):
    if request.method == "POST":
        data = json.loads(request.body)
        result_code = data['Body']['stkCallback']['ResultCode']
        
        if result_code == 0:
            # Payment Successful! 
            # Here you would mark the order as "Paid" in your DB
            print("Payment Received Successfully!")
        else:
            print("Payment Cancelled or Failed")
            
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Success"})
def initiate_stk_push(request):
    if request.method == "POST":
        phone_number = request.POST.get('phone') # Format: 2547xxxxxxxx
        amount = request.POST.get('amount')
        
        access_token = get_access_token()
        password, timestamp = generate_mpesa_password()
        
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(float(amount)),
            "PartyA": phone_number,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone_number,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": "CerealSyncBamburi",
            "TransactionDesc": "Payment for Cereal"
        }
        
        response = requests.post(api_url, json=payload, headers=headers)
        return JsonResponse(response.json())

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
        # 1. Create a snapshot for the receipt BEFORE clearing the session
        receipt_items = []
        total_value = Decimal('0.00')

        for item_id, item in cart.items():
            product = get_object_or_404(Product, id=item_id)
            
            qty = Decimal(str(item['quantity']))
            price = Decimal(str(item['price']))
            subtotal = qty * price
            total_value += subtotal

            # Save to Database

            Sale.objects.create(
                product=product,
                quantity_sold=qty,
                total_price=total
            )

            # Add to our receipt snapshot
            receipt_items.append({
                'name': item['name'],
                'quantity': qty,
                'price': price,
                'subtotal': subtotal
            })
        # 2. Clear the cart session
        request.session['cart'] = {}
        request.session.modified = True

        # 3. Generate a unique receipt number
        receipt_no = str(uuid.uuid4())[:8].upper()
        
        return render(request, 'inventory/success.html',{
            'receipt_items': receipt_items,
            'total_cart_value': total_value,
            'receipt_no': receipt_no,
            'timestamp': timezone.now(),
        })

    except Exception as e:
        print(f"Checkout Error: {e}")
        return redirect('dashboard')