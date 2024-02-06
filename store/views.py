import json
from cmath import inf

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView, TemplateView

from django.shortcuts import render
from django.views.generic import ListView

from django.views.generic import ListView

from config import settings
from .cart import Cart
from .models import Product, Category, Color, ProductPricing, Size, Order, OrderItem

from .forms import CommentForm, ProductSearchForm, AddToCartForm, SelectSizeAndColorForm, OrderForm
from .models import Product, Category, ProductComment, Variant, Image, Tag, Color, AttributeValue, ProductPricing

from colorama import init, Fore, Back, Style

class HomePageView(TemplateView):
    template_name = 'store/home.html'


class CategoryListView(ListView):
    template_name = 'store/category_list.html'
    context_object_name = 'categories'
    queryset = Category.objects.all()


class ProductListView(ListView):
    model = Product
    template_name = 'store/product_list.html'
    context_object_name = 'products'
    paginate_by = 10
    form_class = ProductSearchForm

    def get_queryset(self):
        queryset = super().get_queryset().select_related('category', 'brand').prefetch_related('colors', 'attribute',
                                                                                               'tags', 'price').all()

        category = self.request.GET.get('category')
        color = self.request.GET.get('color')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        reset_filters = self.request.GET.get('reset')
        available = self.request.GET.get('available')

        if category:
            queryset = queryset.filter(category__fa_name=category)
        if color:
            queryset = queryset.filter(colors__en_name=color)
        # اضافه کردن شرط‌ها فقط اگر reset فراخوانی نشده باشد
        if not reset_filters:
            if min_price:
                queryset = queryset.filter(price__price__gte=min_price)
            if max_price:
                queryset = queryset.filter(price__price__lte=max_price)
        elif reset_filters:
            queryset = Product.objects.all()
        # محاسبه موجودی محصول بر اساس مجموع موجودی واریانت‌ها
        queryset = queryset.annotate(total_inventory=Sum('variant__inventory'))

        if available:
            queryset = queryset.filter(total_inventory__gt=0)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(self.request.GET)
        context['categories'] = Category.objects.prefetch_related('children', 'products').all()
        context['colors'] = Color.objects.prefetch_related('products').all()
        context['tags'] = Tag.objects.all()
        cart = Cart(self.request)
        context['cart'] = cart

        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'store/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.select_related('category__parent').prefetch_related('price', 'images', 'attribute',
                                                                                   'attribute__category',
                                                                                   'attribute_values', 'price__color',
                                                                                   'variant__size', 'comments__user', )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_to_cart_form'] = AddToCartForm()
        context['select_size_and_color_form'] = SelectSizeAndColorForm(product_sizes=self.object.sizes.all(), product_colors=self.object.colors.all())

        context['comment_form'] = CommentForm()
        context['product_images'] = self.object.images.all()
        context['attribute_values'] = AttributeValue.objects.select_related('attribute').filter(product_id=self.object.id)
        context['variants'] = Variant.objects.select_related('size').filter(product_id=self.object.id).all()
        related_products = Product.objects.select_related('category__parent').prefetch_related('price__color').filter(
            category=self.object.category).exclude(id=self.object.id)[:6]
        context['related_products'] = related_products
        cart = Cart(self.request)
        context['cart'] = cart


        return context

def cart_detail_view(request):
    cart = Cart(request)

    for item in cart:
        item['product_update_quantity_form'] = AddToCartForm(initial={
            'quantity': item['quantity'],
            'inplace': True,
        })

        item['product_color_and_size_form'] = SelectSizeAndColorForm(initial={
            'color': item['color_id'],
            'size': item['size_id'],
        })

    return render(request, 'store/cart_detail.html', {'cart': cart,})


@require_POST
def add_to_cart_view(request, pk):
    cart = Cart(request)

    product = Product.objects.get(id=pk)
    price = ProductPricing.objects.get(product_id=pk)
    add_to_cart_form = AddToCartForm(request.POST)

    if add_to_cart_form.is_valid():
        add_to_cart_cleaned_data = add_to_cart_form.cleaned_data
        quantity = add_to_cart_cleaned_data['quantity']
        inplace = add_to_cart_cleaned_data['inplace']

        color_and_size_form = SelectSizeAndColorForm(request.POST, product_sizes=product.sizes.all(), product_colors=product.colors.all())
        if color_and_size_form.is_valid():
            color_and_size_cleaned_data = color_and_size_form.cleaned_data
            color_id = color_and_size_cleaned_data['color']
            size_id = color_and_size_cleaned_data['size']

            size_instance = Size.objects.get(id=size_id).title
            color_instance = Color.objects.get(id=color_id).fa_name
            size_identification = Size.objects.get(id=size_id).id
            color_identification = Color.objects.get(id=color_id).id


            cart.add(product, price, color_instance, size_instance, color_identification, size_identification, inplace=inplace, quantity=quantity)
    return redirect('cart_detail')

def cart_clear(request):
    cart = Cart(request)

    if len(cart):
        cart.clear()
        messages.info(request, 'your cart is cleared from the product.')
    else:
        messages.info(request, 'your cart has not any product')

    return redirect('product_list')


def cart_remove(request, pk, product_version_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=pk)
    product_version_id = str(product_version_id)

    # print(Fore.RED + 'Product ID to Remove:', product.id)
    # print(Fore.BLUE + 'Product Version ID to Remove:', product_version_id)

    cart.cart_remove_product(product, product_version_id)

    # Display updated cart information
    # for item in cart:
        # print(Fore.GREEN + 'Product ID in Cart:', item['product_id'])
        # print(Fore.YELLOW + 'Product Version ID in Cart:', item['product_version_id'])
        # print(Fore.CYAN + 'Quantity in Cart:', item['quantity'])

    return redirect('cart_detail')

class CommentCreateView(CreateView):
    model = ProductComment
    form_class = CommentForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        product_id = int(self.kwargs['pk'])
        product = get_object_or_404(Product, id=product_id)
        obj.product = product
        return super().form_valid(form)


@login_required
def order_create_view(request):
    order_form = OrderForm()
    cart = Cart(request)

    if len(cart) == 0:
        messages.warning(request, 'your cart is empty from the product, please first choice some product.')
        return redirect('product_list')

    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            order_obj = order_form.save(commit=False)
            order_obj.customer = request.user
            order_obj.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order_obj,
                    product=item['product_obj'],
                    quantity=item['quantity'],
                    price=item['product_price'],
                )

            cart.clear()

            request.user.first_name = order_obj.first_name
            request.user.last_name = order_obj.last_name
            request.user.save()

            request.session['order_id'] = order_obj.id
            return redirect('payment_process')

    return render(request, 'store/order_create.html', context={'order_form': order_form, 'cart': cart})


def payment_process(request):
    order_id = request.session.get('order_id')

    order_obj = get_object_or_404(Order, id=order_id)


    toman_total_price = order_obj.get_total_price()
    rial_total_price = toman_total_price * 10


    zarinpal_request_url = 'https://api.zarinpal.com/pg/v4/payment/request.json'

    request_header={
        "accept":"application/json",
        "content-type":"application/json"
    }

    request_data={
        'merchant_id': settings.DJANGO_ZARINPAL_MERCHANT_ID,
        'amount':rial_total_price,
        'description': f'#{order_obj.id} : {order_obj.customer.first_name} {order_obj.customer.last_name}',
        'callback_url': request.build_absolute_uri(reverse('payment_callback'))
    }

    res = requests.post(url=zarinpal_request_url, data=json.dumps(request_data), headers=request_header)

    data = res.json()['data']
    authority = data['authority']
    order_obj.zarinpal_authority = authority
    order_obj.save()

    if 'errors' not in data or len(data['errors']) == 0:
        return redirect(f'https://www.zarinpal.com/pg/StartPay/{authority}')
    else:
        return HttpResponse('error form zarinpal')


def payment_callback(request):
    payment_authority = request.GET.get('Authority')
    payments_status = request.GET.get('Status')

    order_obj = get_object_or_404(Order, zarinpal_authority=payment_authority)

    toman_total_price = order_obj.get_total_price()
    rial_total_price = toman_total_price * 10

    if payments_status == 100:
        request_header = {
            'accept': 'application/json',
            'content-type': 'application/json'
        }
        request_data = {
            'merchant_id': settings.DJANGO_ZARINPAL_MERCHANT_ID,
            'amount': rial_total_price,
            'authority': payment_authority,
        }

        res = request.post(url='https://api.zarinpal.com/pg/v4/payment/verify.json', data=json.dumps(request_data), headers=request_header)

        if 'data' in res.json() and ('errors' not in res.json()['data'] or len(res.json()['data']['errors']) == 0):
            data = res.json()['data']
            payment_code = data['code']

            if payment_code == 100:
                order_obj.is_paid = True
                order_obj.zarinpal_ref_id = data['ref_id']
                order_obj.zarinpal_data = data
                order_obj.save()

                return HttpResponse('پرداهت با موفقیت انجام شد')

            elif payment_code == 101:
                return HttpResponse(' این تراکنش قبلا ثبت شده است. این تراکنش از قبل موفقیت آمیز بوده است')

            else:
                error_message = res.json()['errors']['code']
                error_code = res.json()['errors']['message']

                return HttpResponse(f' کد ارور :{error_code} پیغام ارور : {error_message} , پرداخت ناموفق بود ')

    else:
        return HttpResponse('پرداخت ناموفق بود')