from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from products.models import Category, Product


KEEP_PRODUCTS = {
    'roasted-almond-mix-250g': 'roasted_almond_mix.jpg',
    'premium-floor-cleaner-1l': 'floor_cleaner_1l.jpg',
}

NEW_PRODUCTS = [
    ('Staples', 'staples', 'Daily pantry essentials.', 'Wheat Flour 5kg', 'wheat-flour-5kg', 'wheat_flour_5kg.jpg', 310, 279, 42, 'bag', '#F2D8A7'),
    ('Staples', 'staples', 'Daily pantry essentials.', 'Sugar 1kg', 'sugar-1kg', 'sugar_1kg.jpg', 65, 59, 55, 'pouch', '#F7F7F2'),
    ('Staples', 'staples', 'Daily pantry essentials.', 'Sunflower Oil 1L', 'sunflower-oil-1l', 'sunflower_oil_1l.jpg', 175, 159, 35, 'bottle', '#FBBF24'),
    ('Snacks', 'snacks', 'Premium snacks and treats.', 'Potato Chips', 'potato-chips', 'potato_chips.jpg', 55, 49, 70, 'snack', '#F59E0B'),
    ('Snacks', 'snacks', 'Premium snacks and treats.', 'Chocolate Biscuits', 'chocolate-biscuits', 'chocolate_biscuits.jpg', 80, 72, 44, 'box', '#7C2D12'),
    ('Beverages', 'beverages', 'Refreshing drinks and pantry beverages.', 'Orange Juice 1L', 'orange-juice-1l', 'orange_juice_1l.jpg', 130, 115, 40, 'carton', '#F97316'),
    ('Beverages', 'beverages', 'Refreshing drinks and pantry beverages.', 'Instant Coffee', 'instant-coffee', 'instant_coffee.jpg', 280, 249, 28, 'jar', '#92400E'),
    ('Home Care', 'home-care', 'Cleaners and household care.', 'Detergent Powder', 'detergent-powder', 'detergent_powder.jpg', 185, 165, 45, 'box', '#60A5FA'),
    ('Home Care', 'home-care', 'Cleaners and household care.', 'Dishwash Liquid', 'dishwash-liquid', 'dishwash_liquid.jpg', 130, 115, 48, 'bottle', '#84CC16'),
    ('Personal Care', 'personal-care', 'Everyday bath and grooming care.', 'Shampoo Bottle', 'shampoo-bottle', 'shampoo_bottle.jpg', 240, 215, 32, 'bottle', '#38BDF8'),
    ('Personal Care', 'personal-care', 'Everyday bath and grooming care.', 'Bath Soap Pack', 'bath-soap-pack', 'bath_soap_pack.jpg', 125, 110, 46, 'box', '#F9A8D4'),
    ('Personal Care', 'personal-care', 'Everyday bath and grooming care.', 'Toothpaste', 'toothpaste', 'toothpaste.jpg', 110, 95, 52, 'tube', '#EF4444'),
]


class Command(BaseCommand):
    help = 'Deletes old catalog rows/images, keeps two original products, and creates a clean image-backed catalog.'

    def handle(self, *args, **options):
        image_dir = Path(settings.BASE_DIR) / 'static' / 'images' / 'products'
        image_dir.mkdir(parents=True, exist_ok=True)

        keep_files = set(KEEP_PRODUCTS.values())
        new_files = {item[5] for item in NEW_PRODUCTS}
        for image_path in image_dir.glob('*.jpg'):
            if image_path.name not in keep_files:
                image_path.unlink()

        allowed_slugs = set(KEEP_PRODUCTS)
        for category_name, category_slug, description, name, slug, filename, price, sale_price, stock, package_type, color in NEW_PRODUCTS:
            category, _ = Category.objects.update_or_create(
                slug=category_slug,
                defaults={'name': category_name, 'description': description},
            )
            Product.objects.update_or_create(
                slug=slug,
                defaults={
                    'category': category,
                    'name': name,
                    'description': f'{name} from Sai Supermart with clean packaging, dependable quality, and fast local delivery.',
                    'price': price,
                    'sale_price': sale_price,
                    'stock': stock,
                    'image': '',
                    'is_featured': slug in {'wheat-flour-5kg', 'potato-chips', 'orange-juice-1l', 'detergent-powder', 'shampoo-bottle'},
                    'is_active': True,
                },
            )
            self.generate_image(image_dir / filename, name, category_name, package_type, color)
            allowed_slugs.add(slug)

        self.refresh_kept_products()
        Product.objects.exclude(slug__in=allowed_slugs).delete()

        missing = [filename for filename in keep_files | new_files if not (image_dir / filename).exists()]
        if missing:
            raise RuntimeError(f'Missing product images: {", ".join(missing)}')

        self.stdout.write(self.style.SUCCESS(f'Clean catalog ready: {Product.objects.count()} products, {len(keep_files | new_files)} images.'))

    def refresh_kept_products(self):
        snacks, _ = Category.objects.update_or_create(slug='snacks', defaults={'name': 'Snacks', 'description': 'Premium snacks and treats.'})
        home, _ = Category.objects.update_or_create(slug='home-care', defaults={'name': 'Home Care', 'description': 'Cleaners and household care.'})
        Product.objects.update_or_create(
            slug='roasted-almond-mix-250g',
            defaults={
                'category': snacks,
                'name': 'Roasted Almond Mix 250g',
                'description': 'Premium roasted almond mix with dependable quality and fast local delivery.',
                'price': 349,
                'sale_price': 299,
                'stock': 21,
                'image': '',
                'is_featured': True,
                'is_active': True,
            },
        )
        Product.objects.update_or_create(
            slug='premium-floor-cleaner-1l',
            defaults={
                'category': home,
                'name': 'Premium Floor Cleaner 1L',
                'description': 'Fresh home care cleaner with dependable quality and fast local delivery.',
                'price': 189,
                'sale_price': 159,
                'stock': 28,
                'image': '',
                'is_featured': True,
                'is_active': True,
            },
        )

    def generate_image(self, path, name, category, package_type, color):
        size = 1400
        image = Image.new('RGB', (size, size), '#FAFAF8')
        draw = ImageDraw.Draw(image)
        self.draw_background(image)

        if package_type == 'bottle':
            self.draw_bottle(draw, name, category, color)
        elif package_type == 'jar':
            self.draw_jar(draw, name, category, color)
        elif package_type == 'tube':
            self.draw_tube(draw, name, category, color)
        elif package_type == 'carton':
            self.draw_carton(draw, name, category, color)
        elif package_type == 'snack':
            self.draw_snack_packet(draw, name, category, color)
        elif package_type == 'bag':
            self.draw_bag(draw, name, category, color)
        elif package_type == 'pouch':
            self.draw_pouch(draw, name, category, color)
        else:
            self.draw_box(draw, name, category, color)

        image.save(path, quality=94, subsampling=1)

    def draw_background(self, image):
        layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        draw.ellipse((390, 1060, 1010, 1208), fill=(17, 24, 39, 55))
        layer = layer.filter(ImageFilter.GaussianBlur(38))
        image.paste(layer.convert('RGB'), (0, 0), layer)

    def draw_box(self, draw, name, category, color):
        self.rounded_gradient(draw, (440, 300, 960, 1040), 52, color, '#FFFFFF')
        draw.polygon([(960, 300), (1032, 350), (1032, 990), (960, 1040)], fill=self.shade(color, -25))
        draw.polygon([(440, 300), (960, 300), (1032, 350), (510, 350)], fill=self.shade(color, 28))
        self.label(draw, (505, 430, 895, 785), name, category)
        draw.rounded_rectangle((520, 875, 880, 940), radius=28, fill=(255, 255, 255, 190), outline='#FFFFFF')
        draw.text((700, 908), 'Premium Pack', anchor='mm', font=self.font(34, True), fill='#111827')

    def draw_bag(self, draw, name, category, color):
        draw.polygon([(475, 280), (925, 260), (985, 1045), (420, 1045)], fill=self.shade(color, -4), outline='#E5E7EB')
        draw.polygon([(475, 280), (925, 260), (880, 350), (520, 365)], fill=self.shade(color, 28))
        draw.rounded_rectangle((510, 430, 890, 790), radius=56, fill='#FFFFFF', outline='#E5E7EB', width=4)
        self.brand(draw, (700, 500))
        self.multiline_center(draw, name, (700, 625), self.font(58, True), '#111827', max_width=330)
        draw.text((700, 720), category.upper(), anchor='mm', font=self.font(30, True), fill='#6B7280')
        draw.text((700, 925), '5 kg fresh seal', anchor='mm', font=self.font(34, True), fill='#FFFFFF')

    def draw_pouch(self, draw, name, category, color):
        draw.rounded_rectangle((420, 320, 980, 1045), radius=90, fill=self.shade(color, -2), outline='#E5E7EB', width=4)
        draw.polygon([(420, 410), (980, 355), (980, 500), (420, 555)], fill='#FFFFFF')
        self.label(draw, (505, 585, 895, 835), name, category)
        draw.text((700, 935), 'Fresh Pack', anchor='mm', font=self.font(34, True), fill='#111827')

    def draw_snack_packet(self, draw, name, category, color):
        draw.rounded_rectangle((390, 320, 1010, 1040), radius=95, fill=self.shade(color, -4), outline='#E5E7EB', width=4)
        draw.polygon([(390, 430), (1010, 370), (1010, 535), (390, 600)], fill='#FFFFFF')
        draw.ellipse((540, 670, 860, 865), fill=self.shade(color, 32), outline='#FFFFFF', width=8)
        self.brand(draw, (700, 470))
        self.multiline_center(draw, name, (700, 735), self.font(58, True), '#111827', max_width=360)
        draw.text((700, 930), category.upper(), anchor='mm', font=self.font(32, True), fill='#FFFFFF')

    def draw_bottle(self, draw, name, category, color):
        draw.rounded_rectangle((610, 210, 790, 325), radius=32, fill='#E5E7EB')
        draw.rounded_rectangle((560, 305, 840, 1065), radius=108, fill=self.shade(color, -4), outline='#E5E7EB', width=4)
        draw.rectangle((620, 190, 780, 245), fill='#D1D5DB')
        draw.rounded_rectangle((595, 500, 805, 790), radius=48, fill='#FFFFFF', outline='#E5E7EB', width=4)
        draw.line((795, 345, 810, 990), fill=(255, 255, 255), width=14)
        self.brand(draw, (700, 405))
        self.multiline_center(draw, name, (700, 620), self.font(48, True), '#111827', max_width=180)
        draw.text((700, 720), category.upper(), anchor='mm', font=self.font(24, True), fill='#6B7280')
        draw.text((700, 940), '1 L', anchor='mm', font=self.font(42, True), fill='#FFFFFF')

    def draw_carton(self, draw, name, category, color):
        draw.polygon([(470, 330), (850, 275), (980, 420), (600, 480)], fill=self.shade(color, 20), outline='#E5E7EB')
        draw.polygon([(600, 480), (980, 420), (980, 1030), (600, 1090)], fill=self.shade(color, -20), outline='#E5E7EB')
        draw.polygon([(470, 330), (600, 480), (600, 1090), (470, 930)], fill=self.shade(color, 4), outline='#E5E7EB')
        self.label(draw, (625, 550, 930, 820), name, category)
        draw.text((785, 960), '1 L', anchor='mm', font=self.font(46, True), fill='#FFFFFF')

    def draw_jar(self, draw, name, category, color):
        draw.rounded_rectangle((520, 245, 880, 360), radius=36, fill='#111827')
        draw.rounded_rectangle((500, 340, 900, 1035), radius=112, fill=self.shade(color, 3), outline='#E5E7EB', width=4)
        draw.rounded_rectangle((545, 520, 855, 820), radius=54, fill='#FFFFFF', outline='#E5E7EB', width=4)
        draw.line((850, 405, 870, 940), fill=(255, 255, 255), width=16)
        self.brand(draw, (700, 445))
        self.multiline_center(draw, name, (700, 650), self.font(54, True), '#111827', max_width=260)
        draw.text((700, 760), category.upper(), anchor='mm', font=self.font(26, True), fill='#6B7280')

    def draw_tube(self, draw, name, category, color):
        draw.rounded_rectangle((360, 545, 1000, 790), radius=92, fill=self.shade(color, -6), outline='#E5E7EB', width=4)
        draw.rounded_rectangle((940, 560, 1065, 775), radius=38, fill='#E5E7EB')
        draw.rounded_rectangle((450, 585, 760, 750), radius=44, fill='#FFFFFF', outline='#E5E7EB', width=4)
        self.brand(draw, (560, 630))
        self.multiline_center(draw, name, (610, 705), self.font(40, True), '#111827', max_width=250)
        draw.text((850, 675), category.upper(), anchor='mm', font=self.font(28, True), fill='#FFFFFF')

    def label(self, draw, box, name, category):
        draw.rounded_rectangle(box, radius=46, fill='#FFFFFF', outline='#E5E7EB', width=4)
        cx = (box[0] + box[2]) // 2
        self.brand(draw, (cx, box[1] + 70))
        self.multiline_center(draw, name, (cx, box[1] + 155), self.font(52, True), '#111827', max_width=box[2] - box[0] - 70)
        draw.text((cx, box[3] - 60), category.upper(), anchor='mm', font=self.font(28, True), fill='#6B7280')

    def brand(self, draw, center):
        draw.rounded_rectangle((center[0] - 67, center[1] - 30, center[0] + 67, center[1] + 30), radius=24, fill='#22C55E')
        draw.text(center, 'SAI', anchor='mm', font=self.font(34, True), fill='#FFFFFF')

    def rounded_gradient(self, draw, box, radius, start_color, end_color):
        steps = 18
        x1, y1, x2, y2 = box
        start = self.rgb(start_color)
        end = self.rgb(end_color)
        for step in range(steps, 0, -1):
            t = step / steps
            inset = int((1 - t) * 34)
            color = tuple(int(start[i] * t + end[i] * (1 - t)) for i in range(3))
            draw.rounded_rectangle((x1 + inset, y1 + inset, x2 - inset, y2 - inset), radius=max(10, radius - inset), fill=color, outline='#E5E7EB' if step == steps else None, width=4)

    def multiline_center(self, draw, text, center, font, fill, max_width):
        words = text.replace('1L', '1 L').split()
        lines = []
        line = ''
        for word in words:
            candidate = f'{line} {word}'.strip()
            if draw.textlength(candidate, font=font) <= max_width:
                line = candidate
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
        line_height = font.size + 8
        y = center[1] - ((len(lines) - 1) * line_height / 2)
        for line in lines:
            draw.text((center[0], y), line, anchor='mm', font=font, fill=fill)
            y += line_height

    def font(self, size, bold=False):
        paths = [
            'C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf',
            'C:/Windows/Fonts/segoeuib.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf',
        ]
        for path in paths:
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                pass
        return ImageFont.load_default()

    def shade(self, hex_color, amount):
        rgb = list(self.rgb(hex_color))
        rgb = [max(0, min(255, channel + amount)) for channel in rgb]
        return tuple(rgb)

    def rgb(self, hex_color):
        value = hex_color.lstrip('#')
        return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))
