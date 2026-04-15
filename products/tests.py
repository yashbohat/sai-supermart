from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Category, Product


class ProductViewsTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Groceries', slug='groceries', description='Daily essentials')
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            slug='test-product',
            description='Useful item',
            price=Decimal('99.00'),
            stock=10,
            is_featured=True,
        )

    def test_home_page_loads(self):
        response = self.client.get(reverse('products:home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_product_list_loads(self):
        response = self.client.get(reverse('products:list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_product_detail_loads(self):
        response = self.client.get(reverse('products:detail', args=[self.product.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.description)
