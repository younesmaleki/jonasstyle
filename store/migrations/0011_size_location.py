# Generated by Django 4.2 on 2024-01-10 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_alter_attribute_fa_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='size',
            name='location',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]
