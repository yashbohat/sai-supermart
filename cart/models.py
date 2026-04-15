from decimal import Decimal

from django.conf import settings
from django.db import models

from products.models import Offer, Product


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='cart', on_delete=models.CASCADE)
    offer = models.ForeignKey(Offer, null=True, blank=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Cart for {self.user.email}'

    @property
    def subtotal(self):
        return sum((item.total for item in self.items.select_related('product')), Decimal('0.00'))

    @property
    def discount(self):
        return Decimal(str(self.offer.discount_for(self.subtotal))) if self.offer else Decimal('0.00')

    @property
    def total(self):
        return max(Decimal('0.00'), self.subtotal - self.discount)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    @property
    def total(self):
        return self.product.current_price * self.quantity

# Create your models here.
