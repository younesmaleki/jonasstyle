from django.contrib import messages

from store.models import Product, ProductPricing
import uuid

from colorama import init, Fore, Back, Style

class Cart:
    def __init__(self, request):
        self.request = request
        self.session = request.session

        cart = self.session.get('cart')

        if not cart:
            self.session['cart'] = {}
            cart = self.session['cart']

        self.cart = cart

    def add(self, product, price, color, size, color_identification, size_identification, inplace=False, quantity=1):
        product_id = str(product.id)
        product_version_id = str(uuid.uuid4())

        if product_id not in self.cart:
            # اگر محصول در سبد خرید وجود نداشته باشد
            self.cart[product_id] = {
                'product_version_list': [
                    {
                        'product': product.serialize(),
                        'price': price.serialize_price(),
                        'product_id': product.id,
                        'color': color,
                        'color_id': color_identification,
                        'size': size,
                        'size_id': size_identification,
                        'quantity': quantity,
                        'product_version_id': product_version_id,

                    }
                ]
            }
            messages.success(self.request, f'Product "" {product.fa_name} "" successfully added to cart.')
        else:
            # اگر محصول در سبد خرید وجود داشته باشد
            found_product = None
            for product_version in self.cart[product_id]['product_version_list']:
                if (
                        product_version['color'] == color and
                        product_version['size'] == size
                ):
                    # print(Fore.YELLOW + 'add quantity when product is created , quantity : ', quantity)
                    found_product = product_version
                    if inplace:
                        product_version['quantity'] = quantity
                        messages.success(self.request, f'quantity of product "" {product.fa_name} "" successfully updated to " {quantity} ".')
                    else:
                        product_version['quantity'] += quantity
                        messages.success(self.request, f'quantity of product "" {product.fa_name} "" successfully updated and be equal to " {product_version["quantity"]} " ')
                    self.save()
                    break

            if not found_product:
                # اگر نسخه محصول با این رنگ و اندازه وجود نداشته باشد، اضافه کردن به لیست
                self.cart[product_id]['product_version_list'].append({
                    'product': product.serialize(),
                    'price': price.serialize_price(),
                    'product_id': product.id,
                    'color': color,
                    'color_id': color_identification,
                    'size': size,
                    'size_id': size_identification,
                    'quantity': quantity,
                    'product_version_id': product_version_id,

                })
        self.save()


    def save(self):
        self.session.modified = True

    def __iter__(self):
        cart = self.cart.copy()

        product_ids = list(cart.keys())
        products = Product.objects.filter(id__in=product_ids)
        pricings = ProductPricing.objects.filter(product_id__in=product_ids)

        product_dict = {product.id: product for product in products}
        print(Fore.BLUE + 'product dict : ', list(product_dict))
        pricing_dict = {pricing.product_id: pricing for pricing in pricings}
        print(Fore.RED + 'pricing dict : ', list(pricing_dict))

        for product_id, product_info in self.cart.items():
            product_version_list = product_info.get('product_version_list')

            for product_version in product_version_list:
                product_id = product_version['product_id']

                product = product_dict.get(product_id)
                pricing = pricing_dict.get(product_id)

                if product and pricing:
                    yield {
                        'product_version_id': product_version['product_version_id'],
                        'get_total_price_single_product': product_version['quantity'] * pricing.price,
                        'product_obj': product,
                        'product_price': pricing.price,
                        'product_id': product_id,
                        'color': product_version['color'],
                        'color_id': product_version['color_id'],
                        'size': product_version['size'],
                        'size_id': product_version['size_id'],
                        'quantity': product_version['quantity'],
                    }
        self.save()


    def clear(self):
        del self.session['cart']
        self.save()


    def cart_remove_product(self, product, product_version_id):
        product_id_to_remove = str(product.id)

        removed_product = None  # متغیری برای ذخیره محصول حذف شده تعریف می‌کنیم

        for cart_product_id, product_info in list(self.cart.items()):
            product_version_list = product_info.get('product_version_list', [])

            new_product_version_list = []

            for product_version in product_version_list:
                current_product_id = product_version.get('product_id')
                current_product_version_id = product_version.get('product_version_id')

                if current_product_id is not None and current_product_version_id is not None:
                    if str(current_product_id) == str(product_id_to_remove) and str(current_product_version_id) == str(
                            product_version_id):
                        removed_product = product_version
                        print(Fore.GREEN + 'removed product : ', removed_product)
                        continue

                    new_product_version_list.append(product_version)

            if new_product_version_list:
                self.cart[cart_product_id] = {'product_version_list': new_product_version_list}
            else:
                self.cart.pop(cart_product_id)
                messages.info(self.request, f'successfully removed product "" {removed_product["product"]["fa_name"]} "" from the cart')

        self.save()

    def get_total_price(self):
        product_ids = self.cart.keys()

        total_cart_price = []
        for product_id, product_info in self.cart.items():
            product_version_list = product_info.get('product_version_list')

            for product_version in product_version_list:
                total_item_price = product_version['quantity'] * product_version['price']
                total_cart_price.append(total_item_price)

        return sum(total_cart_price)

    def __len__(self):
        count_cart_item = 0

        for product_id, product_info in self.cart.items():
            product_version_list = product_info.get('product_version_list')

            for product_version in product_version_list:
                count_cart_item += 1

        return count_cart_item


    def cart_all_quantity_length(self):
        count_cart_item = 0

        for product_id, product_info in self.cart.items():
            product_version_list = product_info.get('product_version_list')

            for product_version in product_version_list:
                count_cart_item += product_version['quantity']

        return count_cart_item



    def is_empty(self):
        if self.cart:
            return False
        return True

