from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', '0003_order_commission'),
    ]
    operations = [
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('clothes',     'Clothes'),
                    ('books',       'Books'),
                    ('accessories', 'Accessories'),
                ],
            ),
        ),
    ]
