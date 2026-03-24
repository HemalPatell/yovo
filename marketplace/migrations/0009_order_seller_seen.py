from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0008_wishlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='seller_seen',
            field=models.BooleanField(default=False),
        ),
    ]
