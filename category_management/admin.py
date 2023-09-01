from django.contrib import admin
from category_management.models import Category
from django.db import models

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'cat_slug': ('category_name',)}

admin.site.register(Category, CategoryAdmin)
