from django.contrib import admin, messages

# Register your models here.
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from jalali_date.admin import ModelAdminJalaliMixin

from .models import Category, Brand, Attribute, Product, Color, \
    AttributeValue, AttributeCategory, Variant, Image, ProductComment, Tag, Size, ProductPricing, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('fa_name', 'parent', 'created_at')
    list_editable = ('fa_name',)
    list_display_links = ('created_at',)
    list_select_related = ['parent', ]
    list_filter = ['created_at']
    list_per_page = 12
    ordering = ['parent']
    search_fields = ['fa_name__istartswith']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['fa_name', 'description']
    list_display_links = ('description',)
    list_filter = ['fa_name']
    list_per_page = 12
    ordering = ['fa_name']
    search_fields = ['fa_name__istartswith']



@admin.register(AttributeCategory)
class AttributeCategoryAdmin(admin.ModelAdmin):
    list_display = ['fa_name', 'created_at']
    list_display_links = ['created_at']
    list_filter = ['created_at']
    list_per_page = 12
    ordering = ['created_at', ]
    search_fields = ['fa_name__istartswith', ]



class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    fields = ['product', 'value',]
    min_num = 1

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = [ 'fa_name', 'attribute_category', 'category_children', 'category_parent', 'created_at']
    list_display_links = ['created_at']
    list_select_related = ['category__parent', 'attribute_category']
    list_filter = ['fa_name', 'category', 'attribute_category', 'created_at']
    list_per_page = 10
    ordering = ['created_at']
    search_fields = ['fa_name',]
    autocomplete_fields = ['attribute_category', 'category']

    @admin.display(ordering='category__fa_name')
    def category_children(self, product_att):
        return product_att.category.fa_name

    @admin.display(ordering='category__parent')
    def category_parent(self, product_att):
        return product_att.category.parent


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name',]

class VariantInline(admin.TabularInline):
    model = Variant
    fields = ['color', 'inventory', 'size', ]
    extra = 0


class ImageInline(admin.TabularInline):
    model = Image
    fields = ['image', ]
    extra = 0


@admin.register(Product)
class ProductAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ['fa_name', 'product_category', 'is_active', 'slug', 'views', 'num_of_product_comments' ]
    list_editable = ['is_active']
    list_filter = ['created_at', 'category', 'brand', 'gender', 'views']
    list_per_page = 12
    ordering = ['created_at', 'fa_name']
    search_fields = ['fa_name__istartswith', 'category____istartswith', 'brand____istartswith']
    prepopulated_fields = {
        'slug': ['fa_name',]
    }
    autocomplete_fields = ['category', 'brand', 'attribute']
    inlines = [VariantInline, ImageInline]



    @admin.display(ordering='category__fa_name', description='Category')
    def product_category(self, product):
        return product.category.fa_name

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('brand', 'category').prefetch_related(
            'comments').annotate(comments_count=Count('comments')).all()

    @admin.display(ordering='comments_count')
    def num_of_product_comments(self, product):
        url=(
            reverse('admin:store_productcomment_changelist')
            + '?'
            + urlencode({
            'product_id': product.id,
        })
        )
        return format_html('<a href="{}">{}</a>', url, product.comments_count )


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['fa_name', 'en_name', ]
    list_filter = ['fa_name', ]
    list_per_page = 30
    ordering = ['fa_name', ]
    search_fields = ['fa_name__istartswith', ]

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['title',]

@admin.register(ProductPricing)
class ProductPricingAdmin(admin.ModelAdmin):
    list_display = ['product', 'color', 'price']

@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'attribute', 'short_value']
    list_select_related = ['attribute']
    list_filter = ['attribute', ]
    list_per_page = 12
    search_fields = ['attribute__fa_name', 'value']
    autocomplete_fields = ['attribute']

    def short_value(self, obj):
        words = obj.value.split(' ')
        if len(words) > 20:
            return ' '.join(words[:20]) + '...'
        return obj.value

class InventoryFilter(admin.SimpleListFilter):
    LESS_THAN_10 = '<10'
    BETWEEN_10_AND_40 = '11<=40'
    GRATER_THAN_40 = '>40'

    title = 'Critical inventory status'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [(InventoryFilter.LESS_THAN_10, 'warning'), (InventoryFilter.BETWEEN_10_AND_40, 'normal'),
                (InventoryFilter.GRATER_THAN_40, 'excellent'), ]

    def queryset(self, request, queryset):
        if self.value() == InventoryFilter.LESS_THAN_10:
            return queryset.filter(inventory__lt=10)
        if self.value() == InventoryFilter.BETWEEN_10_AND_40:
            return queryset.filter(inventory__range=(10, 40))
        if self.value() == InventoryFilter.GRATER_THAN_40:
            return queryset.filter(inventory__gt=40)



@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'color', 'sku', 'inventory', 'inventory_status']
    list_editable = ['inventory', ]
    list_select_related = ['product', 'color', ]
    list_filter = ['product', 'color', 'inventory', InventoryFilter]
    list_per_page = 12
    ordering = ['product', ]
    search_fields = ['product__fa_name', ]
    actions = ['clear_inventory', ]
    autocomplete_fields = ['color', ]


    @admin.display(description='Clear inventory counts')
    def clear_inventory(self, request, queryset):
        update_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{Count(update_count)} of products inventories cleared to zero',
            messages.SUCCESS
        )

    def inventory_status(self, Product):
        if Product.inventory <= 10:
            return 'low'
        elif Product.inventory > 40:
            return 'high'
        else:
            return 'normal'


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image']
    list_select_related = ['product']
    list_per_page = 12



@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'short_body', 'product_stars', 'comment_status', 'datetime_created', ]
    list_editable = ['comment_status', ]
    list_select_related = ['product', ]
    list_filter = ['product', 'datetime_created', 'product_stars', 'comment_status', ]
    list_per_page = 12
    ordering = ['datetime_created', ]
    search_fields = ['user', 'body', ]
    autocomplete_fields = ['product', ]

    def short_body(self, ProductComment):
        words = ProductComment.body.split(' ')
        if len(words) > 20:
            return ' '.join(words[:20]) + '...'
        return ProductComment.body


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ['order', 'product','quantity', 'price']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer', 'first_name', 'is_paid', 'created_at', 'phone_number']
    inlines = [OrderItemInline,]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']