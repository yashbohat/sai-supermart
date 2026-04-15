from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Category, Product, Wishlist


def home(request):
    categories = Category.objects.all()[:6]
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    return render(request, 'products/home.html', {'categories': categories, 'featured_products': featured_products})


def product_list(request):
    products = Product.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.all()
    category_slug = request.GET.get('category')
    query = request.GET.get('q')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    return render(request, 'products/list.html', {'products': products, 'categories': categories, 'query': query or '', 'category_slug': category_slug or ''})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]
    is_wishlisted = request.user.is_authenticated and Wishlist.objects.filter(user=request.user, product=product).exists()
    return render(request, 'products/detail.html', {'product': product, 'related': related, 'is_wishlisted': is_wishlisted})


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        item.delete()
    return redirect(request.META.get('HTTP_REFERER', product.get_absolute_url()))


@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product', 'product__category')
    return render(request, 'products/wishlist.html', {'items': items})
