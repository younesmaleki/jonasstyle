# Generated by Django 4.2 on 2024-01-18 11:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0017_alter_productcomment_body'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productcomment',
            name='body',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='productcomment',
            name='name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]