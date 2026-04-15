from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.PROTECT)
    name = models.CharField(max_length=180)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.name

    @property
    def current_price(self):
        return self.sale_price or self.price

    @property
    def static_image_path(self):
        """
        Resolves product images from the static catalog.
        Media-backed ImageField files are intentionally bypassed in templates.
        """
        filenames = {
            # Staples
            'wheat-flour-5kg': 'wheat_flour_5kg.jpg',
            'sugar-1kg': 'sugar_1kg.jpg',
            'sunflower-oil-1l': 'sunflower_oil_1l.jpg',
            'salt-1kg': 'salt_1kg.jpg',
            # Snacks
            'potato-chips': 'potato_chips.jpg',
            'chocolate-biscuits': 'chocolate_biscuits.jpg',
            'namkeen-mix': 'namkeen_mix.jpg',
            'energy-bars': 'energy_bars.jpg',
            # Beverages
            'orange-juice-1l': 'orange_juice_1l.jpg',
            'cola-drink': 'cola_drink.jpg',
            'green-tea-pack': 'green_tea_pack.jpg',
            'instant-coffee': 'instant_coffee.jpg',
            # Home Care
            'detergent-powder': 'detergent_powder.jpg',
            'dishwash-liquid': 'dishwash_liquid.jpg',
            'toilet-cleaner': 'toilet_cleaner.jpg',
            'premium-floor-cleaner-1l': 'floor_cleaner_1l.jpg',
            # Personal Care
            'shampoo-bottle': 'shampoo_bottle.jpg',
            'bath-soap-pack': 'bath_soap_pack.jpg',
            'toothpaste': 'toothpaste.jpg',
            # Legacy/Additional
            'roasted-almond-mix-250g': 'roasted_almond_mix.jpg',
        }
        candidates = []

        mapped = filenames.get(self.slug)
        if mapped:
            candidates.append(mapped)

        if self.slug:
            candidates.append(f'{self.slug.replace("-", "_")}.jpg')

        if self.name:
            candidates.append(f'{slugify(self.name).replace("-", "_")}.jpg')

        if self.image:
            candidates.append(Path(self.image.name).name)

        seen = set()
        for filename in candidates:
            if not filename or filename in seen:
                continue
            seen.add(filename)
            relative_path = f'images/products/{filename}'
            if finders.find(relative_path):
                return relative_path

        return ''

    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'slug': self.slug})


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='wishlist_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='wishlisted_by', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.user.email} - {self.product.name}'


class Offer(models.Model):
    DISCOUNT_PERCENT = 'percent'
    DISCOUNT_FIXED = 'fixed'
    DISCOUNT_TYPES = ((DISCOUNT_PERCENT, 'Percent'), (DISCOUNT_FIXED, 'Fixed amount'))

    code = models.CharField(max_length=40, unique=True)
    title = models.CharField(max_length=120)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES, default=DISCOUNT_FIXED)
    discount_value = models.DecimalField(max_digits=8, decimal_places=2)
    active = models.BooleanField(default=True)
    minimum_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.code

    def discount_for(self, subtotal):
        if not self.active or subtotal < self.minimum_order_value:
            return 0
        if self.discount_type == self.DISCOUNT_PERCENT:
            return min(subtotal, subtotal * self.discount_value / 100)
        return min(subtotal, self.discount_value)

# Create your models here.
