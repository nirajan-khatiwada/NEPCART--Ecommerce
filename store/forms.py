from django import forms
from .models import Variation


class ProductCustomSizeColor(forms.Form):
    def __init__(self, product_slug, *args, **kwargs):
        super().__init__(*args, **kwargs)

        variations = Variation.objects.filter(product__slug=product_slug, is_active=True)

        # Extract distinct colors and sizes for this product
        colors = variations.filter(variation_category='color').values_list('variation_value', flat=True).distinct()
        sizes = variations.filter(variation_category='size').values_list('variation_value', flat=True).distinct()

        color_choices = [(val, val.capitalize()) for val in colors]
        size_choices = [(val, val.upper()) for val in sizes]

        if color_choices:
            self.fields['color'] = forms.ChoiceField(
                required=False,
                choices=color_choices,
                widget=forms.Select(attrs={'class': 'form-control'})
            )

        if size_choices:
            self.fields['size'] = forms.ChoiceField(
                required=False,
                choices=size_choices,
                widget=forms.Select(attrs={'class': 'form-control'})
            )