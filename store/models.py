from django.db import models
from django.urls import reverse
from django_mysql.models.functions import JSONField
from django.contrib.auth import get_user_model
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.text import slugify
from django.utils import timezone
from ckeditor.fields import RichTextField


# Create your models here.
from config import settings
from core.models import CustomUser
from django.utils.translation import gettext_lazy as _

class Category(MPTTModel):
    fa_name = models.CharField(max_length=100, verbose_name=_('category'))
    en_name = models.CharField(max_length=100, verbose_name=_('category'))
    parent = TreeForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='children')
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['fa_name']

    def __str__(self):
        return self.fa_name

    def get_absolute_url(self):
        return reverse('category_detail', args=[self.pk])


class Brand(models.Model):
    fa_name = models.CharField(max_length=100, verbose_name=_('brand'))
    en_name = models.CharField(max_length=100, verbose_name=_('brand'))
    description = models.TextField(null=True, blank=True, verbose_name=_('brand description'))
    logo = models.ImageField(upload_to='brand_logo/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fa_name


class AttributeCategory(models.Model):
    fa_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fa_name


class Attribute(models.Model):
    fa_name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='product_attributes')
    attribute_category = models.ForeignKey(AttributeCategory, on_delete=models.PROTECT, related_name='single_attribute')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['fa_name', 'category']

    def __str__(self):
        return self.fa_name


class Color(models.Model):
    fa_name = models.CharField(max_length=100, blank=True, verbose_name=_('color'))
    en_name = models.CharField(max_length=100, blank=True, verbose_name=_('color'))
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.en_name

    def serialize_color(self):
        return self.fa_name


class Size(models.Model):
    title = models.CharField(max_length=50, blank=True, verbose_name=_('size'))

    def __str__(self):
        return self.title

    def serialize_size(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('tags'))

    def __str__(self):
        return self.name


class Product(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other'), ]
    RATE_CHOICES = [('v', 'Very Bad'), ('b', 'Bad'), ('n', 'Normal'), ('g', 'Good'), ('p', 'Perfect')]
    fa_name = models.CharField(max_length=255,verbose_name=_('Farsi Product Name'))
    en_name = models.CharField(max_length=255, blank=True, verbose_name=_('English Product Name'))
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', verbose_name=_('Category'))
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, null=True, blank=True, related_name='products', verbose_name=_('Brand'))
    model = models.CharField(max_length=255, blank=True, verbose_name=_('Product Model'))
    colors = models.ManyToManyField(Color, blank=True, related_name='products', verbose_name=_('Product Colors'))
    sizes = models.ManyToManyField(Size, blank=True, verbose_name=_('Product Sizes'))
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    short_description = models.CharField(max_length=5000, verbose_name=_('Product Short Description'))
    full_description = RichTextField(verbose_name=_('Product Full Description'))
    thumbnail = models.ImageField(upload_to='covers/product_thumbnail/')
    attribute = models.ManyToManyField(Attribute, verbose_name=_('Product Attribute'))
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name=_('Product Gender'))
    is_active = models.BooleanField(default=True)
    tags = models.ManyToManyField(Tag, verbose_name=_('Product Tags'))
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return self.fa_name

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.pk])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.category.fa_name}{self.brand.fa_name}{self.fa_name}')
        super(Product, self).save(*args, **kwargs)

    def serialize(self):
        pricing_info = self.price.serialize_price() if hasattr(self, 'price') else None

        return {
            'id': self.id,
            'fa_name': self.fa_name,
            'en_name': self.en_name,
            'category': self.category.fa_name,
            'brand': self.brand.fa_name if self.brand else '',
            'model': self.model,
            'colors': [color.serialize_color() for color in self.colors.all()],
            'sizes': [size.serialize_size() for size in self.sizes.all()],
            'slug': self.slug,
            'short_description': self.short_description,
            'full_description': self.full_description,
            'thumbnail': self.thumbnail.url,
            'attribute': [attribute.fa_name for attribute in self.attribute.all()],
            'gender': self.get_gender_display(),
            'is_active': self.is_active,
            'tags': [tag.name for tag in self.tags.all()],
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'views': self.views,
            'price': pricing_info,
            # ... دیگر فیلدهای خودتان
        }



class ProductPricing(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='price', verbose_name=_('Product Price'))
    color = models.ForeignKey(Color, on_delete=models.PROTECT, verbose_name=_('Color'))
    price = models.PositiveIntegerField()

    def __str__(self):
        return self.price

    def serialize_price(self):
        return self.price

class AttributeValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='attribute_values')
    attribute = models.ForeignKey(Attribute, on_delete=models.PROTECT, related_name='value')
    value = models.TextField(verbose_name=_('Values of Attribute'))
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.value[:10]


class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='variant', verbose_name=_('Product Variant'))
    color = models.ForeignKey(Color, on_delete=models.PROTECT, related_name='color_variant', verbose_name=_('Color Variant'))
    size = models.ForeignKey(Size, on_delete=models.PROTECT, default='41', related_name='variant_size', verbose_name=_('Size Variant'))
    sku = models.CharField(max_length=80, unique=True, blank=True)
    inventory = models.PositiveIntegerField(default=0, verbose_name=_('Variant Inventory'))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = slugify(f'{self.product.category.fa_name}{self.product.fa_name}{self.color.en_name}{str(self.size.title)}')
        super(Variant, self).save()

    def __str__(self):
        return f'{self.product} : {self.color} : {self.inventory}'


class Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='images')
    image = models.ImageField(upload_to='covers/product_image/', verbose_name=_('Product Image'))
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.fa_name + ' Image'



class ProductComment(models.Model):
    COMMENT_STATUS_WAITING = 'w'
    COMMENT_STATUS_APPROVED = 'a'
    COMMENT_STATUS_CANCEL = 'na'
    COMMENT_STATUS_CHOICES = [(COMMENT_STATUS_WAITING, 'waiting'), (COMMENT_STATUS_APPROVED, 'approved'),
                              (COMMENT_STATUS_CANCEL, 'Not approved')]

    PRODUCT_STARS = (('1', 'Very Bad'), ('2', 'Bad'), ('3', 'normal'), ('4', 'Good'), ('5', 'Perfect'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name=_('Author Comment'))
    body = models.TextField(verbose_name=_('Comment Text'))
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)
    product_stars = models.CharField(max_length=1, choices=PRODUCT_STARS, verbose_name=_('Rate of Product'))
    comment_status = models.CharField(max_length=2, choices=COMMENT_STATUS_CHOICES, default=COMMENT_STATUS_APPROVED)

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.product.pk])


class Order(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_paid = models.BooleanField(_('Is Paid'), default=False)

    first_name = models.CharField(_('First Name'), max_length=100)
    last_name = models.CharField(_('Last name'), max_length=100)
    phone_number = models.CharField(_('Phone Number'), max_length=15)
    email = models.EmailField(_('Email'), )
    address = models.CharField(_('address'), max_length=700)
    order_note = models.CharField(_('Order Note'), max_length=1000, blank=True)
    post_code = models.CharField(_('Post Code'), max_length=25)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    zarinpal_authority = models.CharField(max_length=255, blank=True)
    zarinpal_ref_id = models.CharField(max_length=255, blank=True)
    zarinpal_data = models.TextField()

    def __str__(self):
        return f'order id : {self.id} , created at : {self.created_at}'

    def get_total_price(self):
        return sum(item.quantity * item.price for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)
    price = models.PositiveIntegerField()

    def __str__(self):
        return f'order id : {self.order.id} , product : {self.product.fa_name}, quantity : {self.quantity}, price : {self.price}'





