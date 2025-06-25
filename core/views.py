from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from .forms import PhoneForm, OTPForm
from .models import User, OTP
import random
from .forms import ProfileForm
from .models import Product, Category, User, CartItem, WishlistItem
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods
from .models import Order
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Product, Review
from .forms import ReviewForm
from django.db import models
from .forms import RegisterForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.decorators.http import require_POST
from core.models import Wishlist
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from .models import DeliveryPartner
from .models import OrderItem


def home(request):
    categories = Category.objects.all()
    latest_products = Product.objects.order_by('-id')[:8]
    featured_products = Product.objects.filter(is_featured=True)[:8]

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        wishlist_ids = list(wishlist.products.values_list('id', flat=True))

    return render(request, 'core/home.html', {
        'categories': categories,
        'latest_products': latest_products,
        'featured_products': featured_products,
        'wishlist_ids': wishlist_ids,
    })

def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        referral_code = request.POST.get('referral_code', '').strip().upper()

        if password != confirm_password:
            return render(request, 'core/register.html', {'error': 'Passwords do not match'})

        otp = str(random.randint(1000, 9999))
        print(f"OTP for {phone} is {otp}")

        request.session['reg_data'] = {
            'name': name,
            'email': email,
            'phone': phone,
            'password': make_password(password),
            'referral_code': referral_code,
            'otp': otp,
        }

        return redirect('verify_otp')

    return render(request, 'core/register.html')


User = get_user_model()

def login_phone(request):
    error = ''
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        try:
            user = User.objects.get(phone=phone)
            if user.check_password(password):
                user.backend = 'core.auth_backends.PhoneBackend'
                login(request, user)
                return redirect('home')
            else:
                error = 'Incorrect password.'
        except User.DoesNotExist:
            error = 'Phone number not found.'

    return render(request, 'core/login.html', {'error': error})


User = get_user_model()

def verify_otp(request):
    reg_data = request.session.get('reg_data')
    phone = reg_data.get('phone') if reg_data else request.session.get('phone')
    real_otp = reg_data.get('otp') if reg_data else request.session.get('otp')

    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            if entered_otp == real_otp:
                if reg_data:
                    user, created = User.objects.get_or_create(phone=phone)
                    if created:
                        user.name = reg_data['name']
                        user.email = reg_data['email']
                        user.password = reg_data['password']
                        referral_code = reg_data.get('referral_code')
                        if referral_code:
                            try:
                                referrer = User.objects.get(referral_code=referral_code)
                                user.referred_by = referrer
                                user.wallet_balance += 25
                                referrer.wallet_balance += 50
                                referrer.save()
                            except User.DoesNotExist:
                                pass
                        user.save()
                    request.session.pop('reg_data', None)
                    return redirect('login')
                else:
                    user, _ = User.objects.get_or_create(phone=phone)

                    user.backend = 'core.auth_backends.PhoneBackend'
                    login(request, user)

                    request.session.pop('phone', None)
                    request.session.pop('otp', None)
                    return redirect('home')
    else:
        form = OTPForm()

    return render(request, 'core/verify_otp.html', {'form': form, 'otp': real_otp})


def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def user_profile(request):
    user = request.user

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProfileForm(instance=user)

    referred_users = user.referrals.all()

    return render(request, 'core/profile.html', {
        'form': form,
        'user': user,
        'referred_users': referred_users,
    })

def product_list(request):
    category_id = request.GET.get('category')
    price = request.GET.get('price')
    brand = request.GET.get('brand')
    rating = request.GET.getlist('rating')

    products = Product.objects.all()


    if category_id:
        products = products.filter(category_id=category_id)


    if price and "-" in price:
        try:
            min_price, max_price = map(int, price.split('-'))
            products = products.filter(discount_price__gte=min_price, discount_price__lte=max_price)
        except ValueError:
            pass


    if brand:
        products = products.filter(brand=brand)

    if rating:
        try:
            min_rating = max(map(int, rating))
            products = products.filter(rating__gte=min_rating)
        except ValueError:
            pass


    categories = Category.objects.all()
    brands = Product.objects.values_list('brand', flat=True).distinct()

    wishlist_ids = []
    cart_ids = []
    if request.user.is_authenticated:
        wishlist_ids = list(WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True))
        cart_ids = list(request.user.cartitem_set.values_list('product_id', flat=True))

    selected_category = int(category_id) if category_id and category_id.isdigit() else None

    return render(request, 'core/product_list.html', {
        'products': products,
        'categories': categories,
        'brands': brands,
        'selected_category': selected_category,
        'selected_price': price,
        'selected_brand': brand,
        'selected_ratings': rating,
        'wishlist_ids': wishlist_ids,
        'cart_ids': cart_ids,
    })

@login_required
@require_http_methods(["GET", "POST"])
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.select_related('user').all().order_by('-created_at')
    user_review = None
    form = None

    if request.user.is_authenticated:
        user_review = Review.objects.filter(product=product, user=request.user).first()
        if request.method == 'POST' and not user_review:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.product = product
                review.save()
                return redirect('product_detail', product_id=product.id)
        else:
            form = ReviewForm()

    avg_rating = reviews.aggregate(avg=models.Avg('rating'))['avg']

    return render(request, 'core/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'user_review': user_review,
        'form': form,
        'avg_rating': avg_rating,
    })

@login_required
def add_to_cart(request, product_id):
    user = request.user
    product = Product.objects.get(id=product_id)

    cart_item, created = CartItem.objects.get_or_create(user=user, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()

    return redirect('view_cart')


@login_required
def view_cart(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)
    total = sum(item.total_price for item in cart_items)

    return render(request, 'core/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@csrf_exempt
@login_required
def update_cart(request, item_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        item = CartItem.objects.get(id=item_id, user=request.user)

        if action == 'increase':
            item.quantity += 1
        elif action == 'decrease' and item.quantity > 1:
            item.quantity -= 1
        item.save()
    return redirect('view_cart')


@login_required
def remove_from_cart(request, item_id):
    CartItem.objects.filter(id=item_id, user=request.user).delete()
    return redirect('view_cart')

@login_required
def checkout(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)

    if request.method == 'POST':
        address_option = request.POST.get('address_option')
        phone = request.POST.get('phone')
        payment = request.POST.get('payment')

        if address_option == 'new':
            address = request.POST.get('address')
            user.address = address
            user.phone = phone
            user.save()
        else:
            address = user.address

        order = Order.objects.create(
            user=user,
            address=address,
            payment_method=payment,
            status='Pending' if payment == 'UPI' else 'Placed'
        )

        for cart_item in cart_items:
            print("Creating order item for:", cart_item.product.title)
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.discount_price or cart_item.product.price
            )

        if payment == 'UPI':
            request.session['upi_order_id'] = order.id
            return redirect('upi_payment')

        cart_items.delete()
        return render(request, 'core/order_success.html', {'order': order})

    total = sum((item.product.discount_price or item.product.price) * item.quantity for item in cart_items)

    return render(request, 'core/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'user': user
    })

@login_required
def wishlist_view(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user).select_related('product')
    products = [item.product for item in wishlist_items]
    return render(request, 'core/wishlist.html', {'products': products})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    WishlistItem.objects.get_or_create(user=request.user, product=product)
    return redirect('product_list')

@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item = WishlistItem.objects.filter(user=request.user, product=product)

    if wishlist_item.exists():
        wishlist_item.delete()
    else:
        WishlistItem.objects.create(user=request.user, product=product)

    return redirect('product_list')

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('product_detail', product_id=review.product.id)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'core/edit_review.html', {'form': form, 'product': review.product})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_id = review.product.id
    if request.method == 'POST':
        review.delete()
        return redirect('product_detail', product_id=product_id)
    return render(request, 'core/delete_review_confirm.html', {'review': review})

@login_required
def upi_payment_page(request):
    order_id = request.session.get('upi_order_id')
    if not order_id:
        messages.error(request, "No UPI order found.")
        return redirect('checkout')

    if request.method == 'POST':
        result = request.POST.get('simulate_result')
        if result == 'success':
            order = Order.objects.get(id=order_id, user=request.user)
            order.status = 'Placed'
            order.save()
            CartItem.objects.filter(user=request.user).delete()
            messages.success(request, "UPI Payment Successful!")
            return render(request, 'core/order_success.html', {'order': order})
        else:
            messages.error(request, "Payment failed. Try again.")
            return redirect('upi_payment')

    return render(request, 'core/upi_payment.html')

def delivery_register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('delivery_register')

        if DeliveryPartner.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number already registered")
            return redirect('delivery_register')

        partner = DeliveryPartner.objects.create(
            name=name,
            phone=phone
        )
        partner.set_password(password1)
        partner.save()

        messages.success(request, "Registration successful. Please log in.")
        return redirect('delivery_login')

    return render(request, 'core/delivery_register.html')


def delivery_login(request):
    if request.method == 'POST':
        phone = request.POST['phone']
        password = request.POST['password']
        try:
            partner = DeliveryPartner.objects.get(phone=phone)
            if partner.check_password(password):
                request.session['partner_id'] = partner.id
                return redirect('delivery_dashboard')
            else:
                messages.error(request, "Invalid credentials")
        except DeliveryPartner.DoesNotExist:
            messages.error(request, "Invalid credentials")
    return render(request, 'core/delivery_login.html')



def delivery_logout(request):
    request.session.flush()
    return redirect('delivery_login')


def delivery_dashboard(request):
    partner_id = request.session.get('partner_id')
    if not partner_id:
        return redirect('delivery_login')

    partner = DeliveryPartner.objects.get(id=partner_id)
    orders = Order.objects.filter(delivery_partner=partner)
    return render(request, 'core/delivery_dashboard.html', {'orders': orders})


def update_order_status(request, order_id):
    partner_id = request.session.get('partner_id')
    if not partner_id:
        return redirect('delivery_login')

    order = get_object_or_404(Order, id=order_id, delivery_partner_id=partner_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Order.STATUS_CHOICES):
            order.status = status
            order.save()
            return redirect('delivery_dashboard')

    return render(request, 'core/update_order_status.html', {'order': order, 'status_choices': Order.STATUS_CHOICES})

@login_required
def track_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-order_date')
    return render(request, 'core/track_orders.html', {'orders': orders})

