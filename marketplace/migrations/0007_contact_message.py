from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0006_item_gender'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id',         models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name',  models.CharField(blank=True, max_length=100)),
                ('email',      models.EmailField()),
                ('subject',    models.CharField(
                    choices=[
                        ('general',     'General Question'),
                        ('order',       'Problem with my order'),
                        ('listing',     'Problem with a listing'),
                        ('account',     'Account issue'),
                        ('report',      'Report a user'),
                        ('feature',     'Feature request'),
                        ('partnership', 'Partnership inquiry'),
                        ('other',       'Other'),
                    ],
                    default='general', max_length=20)),
                ('message',    models.TextField()),
                ('is_read',    models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
