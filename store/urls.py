from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('home/', views.HomePageView.as_view(), name='home'),
    path('category_list/', views.CategoryListView.as_view(), name='category_list'),
    path('product_list/', views.ProductListView.as_view(), name='product_list'),
    path('product_detail/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('comments/<int:pk>/', views.CommentCreateView.as_view(), name='comment_create'),
    path('cart_detail/', views.cart_detail_view, name='cart_detail'),
    path('cart_add/<int:pk>/', views.add_to_cart_view, name='cart_add'),
    path('cart_clear/', views.cart_clear, name='cart_clear'),
    path('cart_remove/<int:pk>/<uuid:product_version_id>/', views.cart_remove, name='cart_remove'),
    path('order_create/', views.order_create_view, name='order_create'),
    path('payment_process/', views.payment_process, name='payment_process'),
    path('payment_callback/', views.payment_callback, name='payment_callback'),
]