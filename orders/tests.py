from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from cart.models import CartItem
from products.models import Category, Product

from .models import Order


class OrderFlowTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            email='order@example.com',
            password='strongpass123',
            first_name='Sai',
            phone='9999999999',
            address='42 Market Road',
            city='Hyderabad',
            postal_code='500001',
        )
        self.client.force_login(self.user)
        self.category = Category.objects.create(name='Home Care', slug='home-care', description='Cleaning supplies')
        self.product = Product.objects.create(
            category=self.category,
            name='Cleaner',
            slug='cleaner',
            description='Household cleaner',
            price=Decimal('120.00'),
            stock=8,
        )
        self.client.post(reverse('cart:add', args=[self.product.pk]), {'quantity': 2})

    def test_checkout_creates_order_and_clears_cart(self):
        response = self.client.post(
            reverse('orders:checkout'),
            {
                'full_name': 'Sai Shopper',
                'phone': '9999999999',
                'address': '42 Market Road',
                'city': 'Hyderabad',
                'postal_code': '500001',
            },
            follow=True,
        )

        order = Order.objects.get(user=self.user)
        self.assertRedirects(response, reverse('orders:success', args=[order.pk]))
        self.assertEqual(order.total, Decimal('240.00'))
        self.assertFalse(CartItem.objects.filter(cart__user=self.user).exists())

    def test_order_history_loads(self):
        self.test_checkout_creates_order_and_clears_cart()
        order = Order.objects.get(user=self.user)

        response = self.client.get(reverse('orders:history'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'#{order.pk}')
