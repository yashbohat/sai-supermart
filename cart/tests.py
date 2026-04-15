import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product

from .models import CartItem


class CartFlowTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(email='cart@example.com', password='strongpass123')
        self.client.force_login(self.user)
        self.category = Category.objects.create(name='Snacks', slug='snacks', description='Crunchy things')
        self.product = Product.objects.create(
            category=self.category,
            name='Crunchy Test',
            slug='crunchy-test',
            description='Snack pack',
            price=Decimal('45.00'),
            stock=5,
        )

    def test_add_to_cart_creates_item(self):
        response = self.client.post(reverse('cart:add', args=[self.product.pk]), {'quantity': 2}, follow=True)

        self.assertRedirects(response, reverse('cart:detail'))
        self.assertTrue(CartItem.objects.filter(cart__user=self.user, product=self.product, quantity=2).exists())

    def test_update_quantity_returns_totals(self):
        self.client.post(reverse('cart:add', args=[self.product.pk]), {'quantity': 1})
        item = CartItem.objects.get(cart__user=self.user, product=self.product)

        response = self.client.post(
            reverse('cart:update', args=[item.pk]),
            data=json.dumps({'quantity': 3}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                'ok': True,
                'item_total': '135.00',
                'subtotal': '135.00',
                'discount': '0.00',
                'total': '135.00',
            },
        )
