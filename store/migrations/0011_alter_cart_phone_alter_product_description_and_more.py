# Generated by Django 5.0.4 on 2024-04-19 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_alter_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='phone',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(upload_to='upload/products/'),
        ),
    ]
