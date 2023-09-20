from typing import Iterable, Optional
from django.db import models
from django.urls import reverse
from category_management.models import Category
from django.utils.text import slugify
# Create your models here.


class Product(models.Model):
    product_name = models.CharField(max_length = 200, unique = True)
    brand = models.CharField(max_length = 200, null = True)
    prod_slug = models.SlugField(max_length = 200, unique = True)
    description = models.TextField(max_length = 500, blank = True)
    price = models.DecimalField(max_digits = 10, decimal_places = 2)
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.product_name
    
    def save(self, *args, **kwargs):
        if not self.prod_slug:
            self.prod_slug = slugify(self.product_name)
        super(Product, self).save(*args, **kwargs)
        
    def get_url(self):
        return reverse('product_detail', args = [self.category.cat_slug, self.prod_slug])
    

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to='photos/products', null=True)

    def __str__(self):
        return f"Image {self.id} of {self.product.product_name}"
