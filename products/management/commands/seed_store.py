from django.core.management.base import BaseCommand

from products.models import Category, Offer, Product


class Command(BaseCommand):
    help = 'Seeds Sai Supermart with starter categories, products, and coupons.'

    def handle(self, *args, **options):
        staples, _ = Category.objects.get_or_create(name='Staples', slug='staples', defaults={'description': 'Daily pantry essentials.'})
        fresh, _ = Category.objects.get_or_create(name='Fresh Picks', slug='fresh-picks', defaults={'description': 'Produce and fresh groceries.'})
        home, _ = Category.objects.get_or_create(name='Home Care', slug='home-care', defaults={'description': 'Cleaners and household care.'})
        snacks, _ = Category.objects.get_or_create(name='Snacks', slug='snacks', defaults={'description': 'Premium snacks and treats.'})

        products = [
            (staples, 'Royal Basmati Rice 5kg', 'royal-basmati-rice-5kg', 649, 599, 32, True),
            (staples, 'Cold Pressed Groundnut Oil 1L', 'cold-pressed-groundnut-oil-1l', 289, 259, 24, True),
            (fresh, 'Farm Fresh Apples 1kg', 'farm-fresh-apples-1kg', 220, 199, 18, True),
            (fresh, 'Organic Spinach Bunch', 'organic-spinach-bunch', 55, 45, 35, False),
            (home, 'Premium Floor Cleaner 1L', 'premium-floor-cleaner-1l', 189, 159, 28, True),
            (snacks, 'Roasted Almond Mix 250g', 'roasted-almond-mix-250g', 349, 299, 21, True),
        ]
        for category, name, slug, price, sale_price, stock, featured in products:
            Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'category': category,
                    'name': name,
                    'description': 'Carefully selected for everyday quality, dependable value, and fast local delivery.',
                    'price': price,
                    'sale_price': sale_price,
                    'stock': stock,
                    'is_featured': featured,
                    'is_active': True,
                },
            )

        Offer.objects.get_or_create(code='SAI10', defaults={'title': 'Sai Supermart launch offer', 'discount_type': 'percent', 'discount_value': 10, 'minimum_order_value': 499})
        Offer.objects.get_or_create(code='SAVE50', defaults={'title': 'Flat savings', 'discount_type': 'fixed', 'discount_value': 50, 'minimum_order_value': 999})
        self.stdout.write(self.style.SUCCESS('Seed data ready.'))
