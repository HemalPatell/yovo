from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0004_accessories_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='subcategory',
            field=models.CharField(
                blank=True,
                default='',
                max_length=20,
                choices=[
                    ('tops', 'Tops & T-Shirts'),
                    ('shirts', 'Shirts & Blouses'),
                    ('jeans', 'Jeans & Trousers'),
                    ('dresses', 'Dresses & Skirts'),
                    ('jackets', 'Jackets & Coats'),
                    ('ethnic', 'Ethnic & Traditional'),
                    ('activewear', 'Activewear & Sportswear'),
                    ('winterwear', 'Winterwear & Sweaters'),
                    ('fiction', 'Fiction & Novels'),
                    ('nonfiction', 'Non-Fiction'),
                    ('textbooks', 'Textbooks & Academic'),
                    ('children', "Children's Books"),
                    ('comics', 'Comics & Graphic Novels'),
                    ('selfhelp', 'Self-Help & Motivation'),
                    ('biography', 'Biography & Memoir'),
                    ('science', 'Science & Technology'),
                    ('bags', 'Bags & Backpacks'),
                    ('jewellery', 'Jewellery & Rings'),
                    ('watches', 'Watches'),
                    ('belts', 'Belts & Wallets'),
                    ('sunglasses', 'Sunglasses & Eyewear'),
                    ('footwear', 'Footwear & Shoes'),
                    ('caps', 'Caps & Hats'),
                    ('scarves', 'Scarves & Stoles'),
                ],
            ),
        ),
    ]
