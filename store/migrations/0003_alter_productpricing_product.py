# Generated by Django 4.2 on 2024-01-09 11:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_productpricing'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productpricing',
            name='product',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='price', to='store.product'),
        ),
    ]
