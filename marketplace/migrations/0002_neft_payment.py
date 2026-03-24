from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', '0001_initial'),
    ]
    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(
                max_length=10,
                choices=[
                    ('card', 'Credit/Debit Card'),
                    ('upi',  'UPI'),
                    ('cod',  'Cash on Delivery'),
                    ('neft', 'Bank Transfer / NEFT'),
                ],
                default='cod',
            ),
        ),
    ]
