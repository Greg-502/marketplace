import os
from django.conf import settings
from django.db import models
from django.core.validators import FileExtensionValidator

User = settings.AUTH_USER_MODEL

def marketplace_directory_path(instance, filename):
    name = 'marketplace/products/{0}/{1}'.format(instance.name, filename)
    fullpath = os.path.join(settings.MEDIA_ROOT, name)

    if os.path.exists(fullpath):
        os.remove(fullpath)
    
    return name

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to=marketplace_directory_path)
    slug = models.SlugField(unique=True)

    content_url = models.URLField(blank=True, null=True)
    # content_file = models.FileField(blank=True, null=True, validators=[FileExtensionValidator(allow_extensions=['mp3'])])
    content_file = models.FileField(blank=True, null=True)

    active = models.BooleanField(default=False)

    price = models.PositiveIntegerField(default=100)

    def __str__(self):
        return self.name
    
    def price_display(self):
        return '{0:.2f}'.format(self.price/100)

class PurchasedProduct(models.Model):
    email = models.EmailField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_purchase = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
        