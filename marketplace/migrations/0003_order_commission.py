from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', '0002_neft_payment'),
    ]
    operations = [
        migrations.AddField(
            model_name='order',
            name='commission_fee',
            field=models.DecimalField(max_digits=10, decimal_places=2, default=0),
        ),
    ]
