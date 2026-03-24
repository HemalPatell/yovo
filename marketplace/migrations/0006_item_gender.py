from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0005_item_subcategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='gender',
            field=models.CharField(
                blank=True,
                choices=[
                    ('men',    'Men'),
                    ('women',  'Women'),
                    ('unisex', 'Unisex'),
                    ('kids',   'Kids'),
                ],
                default='',
                max_length=10,
            ),
        ),
    ]
