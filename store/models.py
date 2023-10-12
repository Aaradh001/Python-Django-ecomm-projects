from typing import Iterable, Optional
from django.db import models
from django.urls import reverse
from category_management.models import Category
from django.utils.text import slugify
from django.db.models import UniqueConstraint, Q
from datetime import datetime
# Create your models here.



class Brand(models.Model):
    brand_name = models.CharField(max_length=50,unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.brand_name

        
class Attribute(models.Model):
    attribute_name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.attribute_name

    
# Atribute Value - RED,BLUE
class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    attribute_value = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default = True)

    def __str__(self):
        return self.attribute_value + "-" + self.attribute.attribute_name


class ProductVariantManager(models.Manager):
    """
    Custom manager
    """
    def get_all_variant(self,product):
        variant = super(ProductVariantManager, self).get_queryset().filter(product=product).values('sku_id')
        return variant


class Product(models.Model):
    product_name = models.CharField(max_length = 200, unique = True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand,on_delete=models.SET_NULL,null=True)
    prod_slug = models.SlugField(max_length = 200, unique = True)
    description = models.TextField(max_length = 500, blank = True)
    is_available = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        product_slug_name = f'{self.brand.brand_name}-{self.product_name}-{self.category.category_name}'
        base_slug = slugify(product_slug_name)
        counter = Product.objects.filter(prod_slug__startswith=base_slug).count()
        if counter > 0:
            self.prod_slug = f'{base_slug}-{counter}'
        else:
            self.prod_slug = base_slug
        super(Product, self).save(*args, **kwargs)
        
    def __str__(self):
        return self.brand.brand_name+"-"+self.product_name 


class ProductVariant(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    sku_id = models.CharField(max_length=30)
    attributes = models.ManyToManyField(AttributeValue,related_name='attributes')
    max_price = models.DecimalField(max_digits=8, decimal_places=2)
    sale_price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.IntegerField()
    product_variant_slug = models.SlugField(unique=True, blank=True,max_length=200)
    is_active = models.BooleanField(default=True)
    thumbnail_image = models.ImageField(upload_to='product_variant/images/')
    created_at =models.DateTimeField(auto_now_add=True)
    updated_at =models.DateTimeField(auto_now=True)
    
    
    objects = models.Manager()
    variants = ProductVariantManager()
    
    
    def save(self, *args, **kwargs):
        product_variant_slug_name = f'{self.product.brand.brand_name}-{self.product.product_name}-{self.product.category.category_name}-{self.sku_id}'
        base_slug = slugify(product_variant_slug_name)
        counter = ProductVariant.objects.filter(product_variant_slug__startswith=base_slug).count()
        if counter > 0:
            self.product_variant_slug = f'{base_slug}-{counter}'
        else:
            self.product_variant_slug = base_slug
        super(ProductVariant, self).save(*args, **kwargs)

    
    class Meta:
        constraints = [
            UniqueConstraint(
                name='Unique skuid must be provided',
                fields=['product', 'sku_id'],
                condition=Q(sku_id__isnull=False),
            )
        ]
        
        
    def get_url(self):
        return reverse('product_variant_detail',args=[self.product.category.cat_slug,self.product_variant_slug])
    
    def get_product_name(self):
        return f'{self.product.brand} {self.product.product_name}-{self.sku_id} - ({", ".join([value[0] for value in self.attributes.all().values_list("attribute_value")])},{self.product.category.category_name})'

    def product_price(self):
        offer_percentage=0
       
        #adding catggry offer
        if self.product.category.categoryoffer_set.filter(is_active=True, expire_date__gte=datetime.now()).exists():
                offer_percentage = self.product.category.categoryoffer_set.filter(is_active=True, expire_date__gte=datetime.now()).values_list('discount_percentage', flat=True).order_by('-discount_percentage').first()
                print()
        
        #adding product offer
        if self.productoffer_set.filter(is_active=True, expire_date__gte=datetime.now()).exists():
                offer_percentage = offer_percentage+self.productoffer_set.filter(is_active=True, expire_date__gte=datetime.now()).values_list('discount_percentage', flat=True).order_by('-discount_percentage').first()
        
        if offer_percentage >=100:
            offer_percentage = 100
         
        offer_price =  self.sale_price - self.sale_price * (offer_percentage) / (100)
        return offer_price
    


    def product_offer(self):
        offer_price = {
            'offer_percentage': 0,
            'offer_name': ""
        }
        
        #category offer
        if self.product.product_catg.categoryoffer_set.filter(is_active=True, expire_date__gte=datetime.now()).exists():
            category_offer = self.product.product_catg.categoryoffer_set.filter(is_active=True, expire_date__gte=datetime.now()).order_by('-discount_percentage').first()
            offer_price['offer_percentage'] = category_offer.discount_percentage
            offer_price['offer_name'] = category_offer.offer_name
          
           
        #product_offer
        if self.productoffer_set.filter(is_active=True, expire_date__gte=datetime.now()).exists():
            try:
                product_offer = self.productoffer_set.filter(is_active=True, expire_date__gte=datetime.now()).order_by('-discount_percentage').first()
                
                offer_price['offer_percentage'] += product_offer.discount_percentage
                offer_price['offer_name'] += ","+product_offer.offer_name
            except Exception as e:
                
                print(e)
        if offer_price['offer_percentage'] >=100:
            offer_price['offer_percentage'] = 100
               
        return offer_price



class ProductImage(models.Model):
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to='photos/product_variant', null=True)

    def __str__(self):
        return self.image.url
    



