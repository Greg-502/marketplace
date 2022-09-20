from .models import Product
from django import forms

class ProductForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'max-w-lg block w-full shadow-sm dark:bg-dark-third dark:focus:ring-dark-second focus:ring-indigo-500 dark:focus:border-dark-second dark:text-dark-txt focus:border-indigo-500 sm:max-w-xs sm:text-sm dark:border-dark-second border-gray-300 rounded-md'}), required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'class': 'max-w-lg block w-full shadow-sm dark:bg-dark-third dark:focus:ring-dark-second focus:ring-indigo-500 dark:focus:border-dark-second dark:text-dark-txt focus:border-indigo-500 sm:max-w-xs sm:text-sm dark:border-dark-second border-gray-300 rounded-md'}), required=True)
    slug = forms.CharField(widget=forms.TextInput(attrs={'class': 'max-w-lg block w-full shadow-sm dark:bg-dark-third dark:focus:ring-dark-second focus:ring-indigo-500 dark:focus:border-dark-second dark:text-dark-txt focus:border-indigo-500 sm:max-w-xs sm:text-sm dark:border-dark-second border-gray-300 rounded-r'}), required=True)
    price = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'max-w-lg block w-full shadow-sm dark:bg-dark-third dark:focus:ring-dark-second focus:ring-indigo-500 dark:focus:border-dark-second dark:text-dark-txt focus:border-indigo-500 sm:max-w-xs sm:text-sm dark:border-dark-second border-gray-300 rounded-md'
                }), 
            required=True
                )
    
    content_url = forms.CharField(widget=forms.TextInput(attrs={'class': 'max-w-lg block w-full shadow-sm dark:bg-dark-third dark:focus:ring-dark-second focus:ring-indigo-500 dark:focus:border-dark-second dark:text-dark-txt focus:border-indigo-500 sm:max-w-xs sm:text-sm dark:border-dark-second border-gray-300 rounded-md'}), required=True)

    class Meta:
        model=Product
        fields={
            'name',
            'description',
            'thumbnail',
            'slug',
            'content_url',
            'content_file',
            'price',
            'active',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['thumbnail'].widget.attrs.update({'class': 'sr-only'})
        self.fields['content_file'].widget.attrs.update({'class':'sr-only'})

    def clean_price(self, *args, **kwargs):
        price = self.cleaned_data.get('price')
        price = int(price)

        if price > 99:
            return price
        else:
            raise forms.ValidationError('Pruce must be equal or higuer to $1.')
