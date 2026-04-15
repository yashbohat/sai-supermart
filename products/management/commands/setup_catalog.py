from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from PIL import Image, ImageDraw, ImageFont, ImageFilter

from products.models import Category, Product


CATALOG = [
    ('Staples', 'staples', 'Daily pantry essentials.', 'Wheat Flour 5kg', 'wheat-flour-5kg', 'wheat_flour_5kg.jpg', 310, 279, 42, '#F2E6C9'),
    ('Staples', 'staples', 'Daily pantry essentials.', 'Sugar 1kg', 'sugar-1kg', 'sugar_1kg.jpg', 65, 59, 55, '#F8F8F2'),
    ('Staples', 'staples', 'Daily pantry essentials.', 'Sunflower Oil 1L', 'sunflower-oil-1l', 'sunflower_oil_1l.jpg', 175, 159, 35, '#F9C74F'),
    ('Staples', 'staples', 'Daily pantry essentials.', 'Salt 1kg', 'salt-1kg', 'salt_1kg.jpg', 32, 28, 60, '#E8F3FF'),
    ('Snacks', 'snacks', 'Premium snacks and treats.', 'Potato Chips', 'potato-chips', 'potato_chips.jpg', 55, 49, 70, '#FBBF24'),
    ('Snacks', 'snacks', 'Premium snacks and treats.', 'Chocolate Biscuits', 'chocolate-biscuits', 'chocolate_biscuits.jpg', 80, 72, 44, '#7C2D12'),
    ('Snacks', 'snacks', 'Premium snacks and treats.', 'Namkeen Mix', 'namkeen-mix', 'namkeen_mix.jpg', 95, 85, 38, '#FB923C'),
    ('Snacks', 'snacks', 'Premium snacks and treats.', 'Energy Bars', 'energy-bars', 'energy_bars.jpg', 140, 119, 36, '#8B5CF6'),
    ('Beverages', 'beverages', 'Refreshing drinks and pantry beverages.', 'Orange Juice 1L', 'orange-juice-1l', 'orange_juice_1l.jpg', 130, 115, 40, '#F97316'),
    ('Beverages', 'beverages', 'Refreshing drinks and pantry beverages.', 'Cola Drink', 'cola-drink', 'cola_drink.jpg', 60, 55, 50, '#111827'),
    ('Beverages', 'beverages', 'Refreshing drinks and pantry beverages.', 'Green Tea Pack', 'green-tea-pack', 'green_tea_pack.jpg', 210, 189, 30, '#22C55E'),
    ('Beverages', 'beverages', 'Refreshing drinks and pantry beverages.', 'Instant Coffee', 'instant-coffee', 'instant_coffee.jpg', 280, 249, 28, '#92400E'),
    ('Home Care', 'home-care', 'Cleaners and household care.', 'Detergent Powder', 'detergent-powder', 'detergent_powder.jpg', 185, 165, 45, '#60A5FA'),
    ('Home Care', 'home-care', 'Cleaners and household care.', 'Dishwash Liquid', 'dishwash-liquid', 'dishwash_liquid.jpg', 130, 115, 48, '#84CC16'),
    ('Home Care', 'home-care', 'Cleaners and household care.', 'Toilet Cleaner', 'toilet-cleaner', 'toilet_cleaner.jpg', 145, 129, 34, '#2563EB'),
    ('Personal Care', 'personal-care', 'Everyday bath and grooming care.', 'Shampoo Bottle', 'shampoo-bottle', 'shampoo_bottle.jpg', 240, 215, 32, '#38BDF8'),
    ('Personal Care', 'personal-care', 'Everyday bath and grooming care.', 'Bath Soap Pack', 'bath-soap-pack', 'bath_soap_pack.jpg', 125, 110, 46, '#F9A8D4'),
    ('Personal Care', 'personal-care', 'Everyday bath and grooming care.', 'Toothpaste', 'toothpaste', 'toothpaste.jpg', 110, 95, 52, '#EF4444'),
]

KEEP_EXISTING = {'roasted-almond-mix-250g', 'premium-floor-cleaner-1l'}


class Command(BaseCommand):
    help = 'Builds the expanded Sai Supermart catalog and generates static product mockup images.'

    def handle(self, *args, **options):
        image_dir = Path(settings.BASE_DIR) / 'static' / 'images' / 'products'
        image_dir.mkdir(parents=True, exist_ok=True)

        allowed_slugs = set(KEEP_EXISTING)
        for category_name, category_slug, category_description, name, slug, filename, price, sale_price, stock, color in CATALOG:
            category, _ = Category.objects.get_or_create(
                slug=category_slug,
                defaults={'name': category_name, 'description': category_description},
            )
            Category.objects.filter(pk=category.pk).update(name=category_name, description=category_description)
            Product.objects.update_or_create(
                slug=slug,
                defaults={
                    'category': category,
                    'name': name,
                    'description': f'{name} with clean packaging, dependable quality, and fast local delivery from Sai Supermart.',
                    'price': price,
                    'sale_price': sale_price,
                    'stock': stock,
                    'is_featured': slug in {'wheat-flour-5kg', 'potato-chips', 'orange-juice-1l', 'detergent-powder', 'shampoo-bottle'},
                    'is_active': True,
                },
            )
            self.generate_product_image(image_dir / filename, name, category_name, color)
            allowed_slugs.add(slug)

        Product.objects.exclude(slug__in=allowed_slugs).update(is_active=False, is_featured=False)
        self.stdout.write(self.style.SUCCESS(f'Catalog ready with {len(allowed_slugs)} active products.'))

    def generate_product_image(self, path, name, category, color):
        if path.exists():
            return

        canvas_size = 1000
        image = Image.new('RGB', (canvas_size, canvas_size), '#FFFFFF')
        draw = ImageDraw.Draw(image)
        font_bold = self.font(64, bold=True)
        font_medium = self.font(34, bold=False)
        font_small = self.font(26, bold=False)

        shadow = Image.new('RGBA', (canvas_size, canvas_size), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle((275, 740, 725, 805), radius=80, fill=(17, 24, 39, 58))
        shadow = shadow.filter(ImageFilter.GaussianBlur(34))
        image.paste(shadow.convert('RGB'), (0, 0), shadow)

        if category in {'Beverages', 'Home Care', 'Personal Care'} and 'Pack' not in name:
            self.draw_bottle(draw, color, name, category, font_bold, font_medium, font_small)
        elif 'Bars' in name or 'Biscuits' in name or 'Soap' in name or 'Chips' in name or 'Namkeen' in name:
            self.draw_pouch(draw, color, name, category, font_bold, font_medium, font_small)
        else:
            self.draw_box(draw, color, name, category, font_bold, font_medium, font_small)

        image.save(path, quality=92)

    def draw_box(self, draw, color, name, category, font_bold, font_medium, font_small):
        draw.rounded_rectangle((310, 215, 690, 760), radius=38, fill=color, outline='#E5E7EB', width=3)
        draw.rounded_rectangle((340, 250, 660, 350), radius=28, fill='#FFFFFF')
        draw.rounded_rectangle((340, 400, 660, 575), radius=30, fill='#FFFFFF')
        draw.text((500, 285), 'SAI', anchor='mm', font=font_bold, fill='#16A34A')
        draw.text((500, 445), self.short_title(name), anchor='mm', font=font_medium, fill='#111827')
        draw.text((500, 510), category.upper(), anchor='mm', font=font_small, fill='#6B7280')
        draw.text((500, 690), 'Premium Pack', anchor='mm', font=font_small, fill='#111827')

    def draw_pouch(self, draw, color, name, category, font_bold, font_medium, font_small):
        draw.rounded_rectangle((250, 265, 750, 745), radius=70, fill=color, outline='#E5E7EB', width=3)
        draw.polygon([(250, 330), (750, 300), (750, 390), (250, 420)], fill='#FFFFFF')
        draw.rounded_rectangle((315, 465, 685, 610), radius=34, fill='#FFFFFF')
        draw.text((500, 352), 'SAI', anchor='mm', font=font_bold, fill='#16A34A')
        draw.text((500, 515), self.short_title(name), anchor='mm', font=font_medium, fill='#111827')
        draw.text((500, 570), category.upper(), anchor='mm', font=font_small, fill='#6B7280')
        draw.text((500, 685), 'Fresh Crunch', anchor='mm', font=font_small, fill='#FFFFFF')

    def draw_bottle(self, draw, color, name, category, font_bold, font_medium, font_small):
        draw.rounded_rectangle((425, 165, 575, 245), radius=25, fill='#E5E7EB')
        draw.rounded_rectangle((370, 230, 630, 760), radius=80, fill=color, outline='#E5E7EB', width=3)
        draw.rounded_rectangle((395, 380, 605, 585), radius=34, fill='#FFFFFF')
        draw.text((500, 315), 'SAI', anchor='mm', font=font_bold, fill='#FFFFFF')
        draw.text((500, 455), self.short_title(name), anchor='mm', font=font_medium, fill='#111827')
        draw.text((500, 520), category.upper(), anchor='mm', font=font_small, fill='#6B7280')
        draw.text((500, 690), 'Daily Care', anchor='mm', font=font_small, fill='#FFFFFF')

    def short_title(self, text):
        words = text.replace('1L', '1 L').replace('5kg', '5 kg').split()
        if len(words) <= 2:
            return text
        return ' '.join(words[:2])

    def font(self, size, bold=False):
        candidates = [
            'C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf',
            'C:/Windows/Fonts/segoeuib.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf',
        ]
        for path in candidates:
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                pass
        return ImageFont.load_default()
