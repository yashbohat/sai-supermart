import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Offer, Product

from .models import Cart, CartItem


def get_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def cart_detail(request):
    cart = get_cart(request.user)
    items = cart.items.select_related('product', 'product__category')
    return render(request, 'cart/detail.html', {'cart': cart, 'items': items})


@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = get_cart(request.user)
    quantity = max(1, int(request.POST.get('quantity', 1)))
    item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})
    if not created:
        item.quantity = min(product.stock or 99, item.quantity + quantity)
        item.save()
    return redirect('cart:detail')


@login_required
@require_POST
def update_quantity(request, item_id):
    cart = get_cart(request.user)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    payload = json.loads(request.body.decode() or '{}') if request.body else request.POST
    quantity = max(0, int(payload.get('quantity', item.quantity)))
    if quantity == 0:
        item.delete()
        item_total = 0
    else:
        item.quantity = min(item.product.stock or 99, quantity)
        item.save()
        item_total = item.total
    return JsonResponse({'ok': True, 'item_total': f'{item_total:.2f}', 'subtotal': f'{cart.subtotal:.2f}', 'discount': f'{cart.discount:.2f}', 'total': f'{cart.total:.2f}'})


@login_required
@require_POST
def apply_coupon(request):
    cart = get_cart(request.user)
    code = request.POST.get('code', '').strip().upper()
    offer = Offer.objects.filter(code__iexact=code, active=True).first()
    if offer and offer.discount_for(cart.subtotal):
        cart.offer = offer
        cart.save()
    return redirect('cart:detail')


@login_required
@require_POST
def remove_coupon(request):
    cart = get_cart(request.user)
    cart.offer = None
    cart.save()
    return redirect('cart:detail')
