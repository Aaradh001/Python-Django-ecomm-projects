from django.contrib import admin
from .models import Account, UserProfile, AddressBook
# Register your models here.



admin.site.register(Account)
admin.site.register(UserProfile)
admin.site.register(AddressBook)