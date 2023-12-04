import json

from django import forms
from django.core.exceptions import ValidationError

from orders.models import Order
from store.models import Product, ProductGallery
from utils.files import validate_file_size, crop_image


class ChangePasswordForm(forms.Form):
    new_password1 = forms.CharField(max_length=254)
    new_password2 = forms.CharField(max_length=254)

    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 != new_password2:
            self.add_error('new_password2', 'Passwords do not match.')


class AddProductForm(forms.ModelForm):
    variations = forms.CharField(max_length=5000)
    is_available = forms.CharField(max_length=50)
    image_x = forms.FloatField(widget=forms.HiddenInput())
    image_y = forms.FloatField(widget=forms.HiddenInput())
    image_w = forms.FloatField(widget=forms.HiddenInput())
    image_h = forms.FloatField(widget=forms.HiddenInput())
    images = forms.ImageField(validators=[validate_file_size])

    class Meta:
        model = Product
        fields = [
            'product_name', 'description', 'price', 'stock',
            'category', 'is_available', 'variations', 'image_x', 'image_y',
            'image_w', 'image_h', 'images', 'location', 'Datetime',
        ]

    def clean_is_available(self):
        val = self.cleaned_data.get('is_available')
        if val == 'available':
            return True
        elif val == 'not_available':
            return False
        else:
            raise ValidationError('Invalid data.')

    def clean_variations(self):
        val = self.cleaned_data.get('variations')
        if not val:
            return []

        val = json.loads(val)
        categories = []
        for i in range(len(val['categories'])):
            var_cat = val['categories'][i]
            var_val = val['values'][i]

            if var_cat not in ['color', 'size']:
                raise ValidationError(f'{var_cat} is not a valid variation category.')

            if len(var_val) > 100:
                raise ValidationError(f'{var_val} is too long for variation value.')

            categories.append({
                'category': var_cat,
                'value': var_val,
            })

        return categories

    def save(self, *args, **kwargs):
        product = super(AddProductForm, self).save()

        # Crop image
        data = {
            'x': self.cleaned_data['image_x'],
            'y': self.cleaned_data['image_y'],
            'w': self.cleaned_data['image_w'],
            'h': self.cleaned_data['image_h'],
            'width': 480, 'height': 480
        }
        crop_image(product.images, data)

        return product


class ProductImgForm(forms.ModelForm):
    image_x = forms.FloatField(widget=forms.HiddenInput())
    image_y = forms.FloatField(widget=forms.HiddenInput())
    image_w = forms.FloatField(widget=forms.HiddenInput())
    image_h = forms.FloatField(widget=forms.HiddenInput())
    images = forms.ImageField(validators=[validate_file_size])

    class Meta:
        model = Product
        fields = [
            'image_x', 'image_y', 'image_w', 'image_h', 'images',
        ]

    def save(self, *args, **kwargs):
        product = super(ProductImgForm, self).save()

        # Crop image
        data = {
            'x': self.cleaned_data['image_x'],
            'y': self.cleaned_data['image_y'],
            'w': self.cleaned_data['image_w'],
            'h': self.cleaned_data['image_h'],
            'width': 480, 'height': 480
        }
        crop_image(product.images, data)

        return product


class ProductDetailsForm(forms.ModelForm):
    is_available = forms.CharField(max_length=50)
    variations = forms.CharField(max_length=5000)

    class Meta:
        model = Product
        fields = [
            'product_name', 'category', 'price', 'is_available',
            'stock', 'description', 'variations', 'location', 'Datetime',
        ]

    def clean_is_available(self):
        val = self.cleaned_data.get('is_available')

        if val == 'available':
            return True
        elif val == 'not_available':
            return False
        else:
            raise ValidationError('Invalid data.')

    def clean_variations(self):
        val = self.cleaned_data.get('variations')
        if not val:
            return []

        val = json.loads(val)
        categories = []
        for i in range(len(val['categories'])):
            var_cat = val['categories'][i]
            var_val = val['values'][i]

            if var_cat not in ['color', 'size']:
                raise ValidationError(f'{var_cat} is not a valid variation category.')

            if len(var_val) > 100:
                raise ValidationError(f'{var_val} is too long for variation value.')

            categories.append({
                'category': var_cat,
                'value': var_val,
            })

        return categories


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']


class ProductGalleryImgForm(forms.ModelForm):
    image_x = forms.FloatField(widget=forms.HiddenInput())
    image_y = forms.FloatField(widget=forms.HiddenInput())
    image_w = forms.FloatField(widget=forms.HiddenInput())
    image_h = forms.FloatField(widget=forms.HiddenInput())
    image = forms.ImageField(validators=[validate_file_size])

    class Meta:
        model = ProductGallery
        fields = [
            'image_x', 'image_y', 'image_w', 'image_h', 'image',
        ]

    def save(self, *args, **kwargs):
        img = super(ProductGalleryImgForm, self).save()

        # Crop image
        data = {
            'x': self.cleaned_data['image_x'],
            'y': self.cleaned_data['image_y'],
            'w': self.cleaned_data['image_w'],
            'h': self.cleaned_data['image_h'],
            'width': 480, 'height': 480
        }
        crop_image(img.image, data)

        return img
