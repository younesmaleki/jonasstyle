from django.forms.models import ModelForm
from .models import ProductComment, Category, Color, Product, Order
from django import forms

from .serializers import SizeSerializer, ColorSerializer


class CommentForm(ModelForm):
    class Meta:
        model = ProductComment
        fields = ['body', 'product_stars']



class ProductSearchForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, label='دسته بندی')
    color = forms.ModelChoiceField(queryset=Color.objects.all(), required=False, label='رنگ')
    min_price = forms.IntegerField(required=False, label='حداقل قیمت')
    max_price = forms.IntegerField(required=False, label='حداکثر قیمت')
    available = forms.BooleanField(required=False, label='موجود بودن')


class AddToCartForm(forms.Form):
    QUANTITY_CHOICES = [(i, str(i)) for i in range(1,31)]

    quantity = forms.TypedChoiceField(choices=QUANTITY_CHOICES, coerce=int)
    inplace = forms.BooleanField(required=False, widget=forms.HiddenInput)


class SelectSizeAndColorForm(forms.Form):
    size = forms.ChoiceField(choices=[], label='Select Size')
    color = forms.ChoiceField(choices=[], label='Select Color')

    def __init__(self, *args, **kwargs):
        product_sizes = kwargs.pop('product_sizes', [])
        product_colors = kwargs.pop('product_colors', [])
        super(SelectSizeAndColorForm, self).__init__(*args, **kwargs)

        size_choices = SizeSerializer(product_sizes, many=True).data
        color_choices = ColorSerializer(product_colors, many=True).data

        self.fields['size'].choices = [(size['id'], size['title']) for size in size_choices]
        self.fields['color'].choices = [(color['id'], color['fa_name']) for color in color_choices]


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'address', 'post_code', 'order_note']

        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'order_note': forms.Textarea(attrs={'rows': 5, 'placeholder': 'if you have any note please write here '})
        }
