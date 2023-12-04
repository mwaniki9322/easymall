from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import F
from django.db.models.functions import Cast
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View

from accounts.models import Account, UserProfile
from category.models import Category
from custom_admin.forms import ChangePasswordForm, AddProductForm, ProductImgForm, ProductDetailsForm, OrderStatusForm, \
    ProductGalleryImgForm
from orders.models import Payment, Order, OrderProduct
from store.models import Variation, Product, ProductGallery
from django.db import models


def is_admin_check(user):
    return user.is_admin


@login_required
@user_passes_test(is_admin_check)
def index_view(request):
    sales = OrderProduct.objects.filter(
        order__is_ordered=True, order__status='Completed'
    ).aggregate(models.Sum('product_price'))
    context = {
        'orders': Order.objects.filter(is_ordered=True).count(),
        'products': Product.objects.count(),
        'sales': sales['product_price__sum'] if sales.get('product_price__sum') else 0,
    }
    return render(request, 'custom_admin/index.html', context)


@login_required
@user_passes_test(is_admin_check)
def users_view(request):
    accounts_q = Account.objects.order_by('-date_joined')
    paginator = Paginator(accounts_q, 20)  # 20 per page.
    page_number = request.GET.get('page')
    accounts = paginator.get_page(page_number)

    context = {
        'accounts': accounts
    }
    return render(request, 'custom_admin/users.html', context)


@login_required
@user_passes_test(is_admin_check)
def single_user_view(request, pk):
    account = get_object_or_404(Account, pk=pk)
    context = {
        'account': account,
        'profile': UserProfile.objects.filter(user=account).first()
    }
    return render(request, 'custom_admin/single_user.html', context)


@login_required
@user_passes_test(is_admin_check)
@require_POST
def change_user_password_view(request, pk):
    user = get_object_or_404(Account, pk=pk)
    form = ChangePasswordForm(data=request.POST)
    if form.is_valid():
        user.set_password(form.cleaned_data['new_password1'])
        user.save()

        data = {
            'message': 'Password changed successful',
            'callback': 'form_reset',
        }
        return JsonResponse(data=data, status=200)
    else:
        return JsonResponse({'errors': form.errors}, status=400)


@login_required
@user_passes_test(is_admin_check)
@require_POST
def delete_user_view(request, pk):
    Account.objects.filter(pk=pk).delete()
    messages.success(request, 'Account deleted successfully.')
    return redirect('admin_users')


@login_required
@user_passes_test(is_admin_check)
def products_view(request):
    products_q = Product.objects.order_by('-created_date')
    paginator = Paginator(products_q, 15)  # 15 per page.
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context = {
        'products': products
    }
    return render(request, 'custom_admin/products.html', context)


class AddProductView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        return is_admin_check(self.request.user)

    def get(self, request):
        categories = Category.objects.order_by('category_name')
        context = {
            'categories': categories
        }
        return render(self.request, 'custom_admin/add_product.html', context)

    def post(self, request):
        form = AddProductForm(data=self.request.POST, files=self.request.FILES)
        if not form.is_valid():
            # Invalid data
            msg = 'Submitted data has errors. Please try again.'
            return JsonResponse({'errors': form.errors, 'message': msg}, status=400)

        variations = form.cleaned_data['variations']

        # Save product
        product = form.save()

        # Create variations
        vars_list = []
        for var in variations:
            vars_list.append(
                Variation(
                    product=product,
                    variation_category=var['category'],
                    variation_value=var['value'],
                )
            )

        if vars_list:
            # Bulk create variables
            Variation.objects.bulk_create(vars_list)

        messages.success(self.request, 'Product added successfully.')
        return HttpResponse(status=200)


class ManageProductView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        return is_admin_check(self.request.user)

    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        categories = Category.objects.order_by('category_name')
        variations = Variation.objects.filter(product=product)
        gallery = ProductGallery.objects.filter(product=product)
        context = {
            'product': product,
            'categories': categories,
            'variations': variations,
            'gallery': gallery,
        }
        return render(self.request, 'custom_admin/manage_product.html', context)

    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        form_class = self.request.POST['form']
        form_classes = {
            'product_details': ProductDetailsForm(instance=product, data=self.request.POST),
            'product_img': ProductImgForm(instance=product, data=self.request.POST, files=self.request.FILES),
            'gallery_img': ProductGalleryImgForm(data=self.request.POST, files=self.request.FILES)
        }

        form = form_classes[form_class]

        if not form.is_valid():
            # Invalid data
            return JsonResponse({'errors': form.errors}, status=400)

        if form_class == 'product_img':
            form.save()
            return JsonResponse(data={'image': product.images.url}, status=200)

        elif form_class == 'gallery_img':
            img = form.save(commit=False)
            img.product = product
            img.save()
            return JsonResponse(data={'callback': 'reload'}, status=200)

        elif form_class == 'product_details':
            variations = form.cleaned_data['variations']

            # Update product
            form.save()

            # Prepare variations
            vars_list = []
            for var in variations:
                vars_list.append(
                    Variation(
                        product=product,
                        variation_category=var['category'],
                        variation_value=var['value'],
                    )
                )

            # Delete current variations
            Variation.objects.filter(product=product).delete()

            if vars_list:
                # Bulk create new variations
                Variation.objects.bulk_create(vars_list)

            messages.success(self.request, 'Product updated successfully')
            return JsonResponse(data={'callback': 'reload'}, status=200)

        else:
            raise PermissionDenied


@login_required
@user_passes_test(is_admin_check)
@require_POST
def delete_product_view(request, slug):
    Product.objects.filter(slug=slug).delete()
    messages.success(request, 'Product deleted successfully.')
    return JsonResponse(data={'next_url': reverse_lazy('admin_products')}, status=200)


@login_required
@user_passes_test(is_admin_check)
@require_POST
def delete_gallery_img_view(request):
    ProductGallery.objects.filter(pk=request.POST['img']).delete()
    return HttpResponse(status=200)


@login_required
@user_passes_test(is_admin_check)
def payments_view(request):
    payments_q = Payment.objects.order_by('-created_at')
    paginator = Paginator(payments_q, 20)  # 20 per page.
    page_number = request.GET.get('page')
    payments = paginator.get_page(page_number)

    context = {
        'payments': payments
    }
    return render(request, 'custom_admin/payments.html', context)


@login_required
@user_passes_test(is_admin_check)
def orders_view(request):
    orders_q = Order.objects.filter(is_ordered=True).order_by('-created_at')
    paginator = Paginator(orders_q, 20)  # 20 per page.
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)

    context = {
        'orders': orders
    }
    return render(request, 'custom_admin/orders.html', context)


@login_required
@user_passes_test(is_admin_check)
def single_order_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    products = OrderProduct.objects.filter(order=order)
    context = {
        'order': order,
        'products': products,
    }
    return render(request, 'custom_admin/single_order.html', context)


@login_required
@user_passes_test(is_admin_check)
@require_POST
def change_order_status_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    form = OrderStatusForm(data=request.POST, instance=order)

    if not form.is_valid():
        # Invalid data
        return JsonResponse({'errors': form.errors}, status=400)

    form.save()

    messages.success(request, 'Order status changed successfully.')
    return JsonResponse(data={'next_url': reverse_lazy('admin_orders')}, status=200)
