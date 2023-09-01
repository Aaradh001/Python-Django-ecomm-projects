from django.db import models
from django.utils.text import slugify
from django.urls import reverse

# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    cat_slug = models.SlugField(unique=True)
    is_valid = models.BooleanField(default=True)
    
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    
    
    def __str__(self):
        return self.category_name
    
    
    def save(self, *args, **kwargs):
        if not self.cat_slug:
            self.cat_slug = slugify(self.category_name)
        super(Category, self).save(*args, **kwargs)
    
    
    def get_url(self):
        return reverse('product_by_category', args = [self.cat_slug])