from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from cart.views import get_cart

from .models import Order, OrderItem


@login_required
def checkout(request):
    cart = get_cart(request.user)
    items = cart.items.select_related('product')
    if not items.exists():
        return redirect('cart:detail')
    if request.method == 'POST':
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                full_name=request.POST.get('full_name') or request.user.get_full_name() or request.user.email,
                phone=request.POST.get('phone') or request.user.phone,
                address=request.POST.get('address') or request.user.address,
                city=request.POST.get('city') or request.user.city,
                postal_code=request.POST.get('postal_code') or request.user.postal_code,
                coupon_code=cart.offer.code if cart.offer else '',
                subtotal=cart.subtotal,
                discount=cart.discount,
                total=cart.total,
            )
            for item in items:
                OrderItem.objects.create(order=order, product=item.product, product_name=item.product.name, price=item.product.current_price, quantity=item.quantity)
                item.product.stock = max(0, item.product.stock - item.quantity)
                item.product.save(update_fields=['stock'])
            cart.items.all().delete()
            cart.offer = None
            cart.save()
        return redirect('orders:success', pk=order.pk)
    return render(request, 'orders/checkout.html', {'cart': cart, 'items': items})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'orders/history.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related('items'), pk=pk, user=request.user)
    return render(request, 'orders/detail.html', {'order': order})


@login_required
def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'orders/success.html', {'order': order})


@login_required
@require_POST
def cancel_order(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related('items__product'), pk=pk, user=request.user)
    if not order.can_cancel:
        messages.error(request, 'This order can no longer be cancelled.')
        return redirect('orders:detail', pk=order.pk)
    with transaction.atomic():
        order.status = Order.STATUS_CANCELLED
        order.save(update_fields=['status'])
        for item in order.items.all():
            item.product.stock += item.quantity
            item.product.save(update_fields=['stock'])
    messages.success(request, f'Order #{order.pk} has been cancelled.')
    return redirect('orders:detail', pk=order.pk)
