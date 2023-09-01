from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid

# Create your models here.

class MyAccountManager(BaseUserManager):
    
    def create_user(self, first_name, last_name, phone_number, email, password = None):
        if not email:
            raise ValueError("Email address is mandatory")
        if not password:
            raise ValueError("password is mandatory")
        
        
        user = self.model(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            phone_number = phone_number,
        )

        user.set_password(password)
        user.save(using = self._db)
        return user
    
    
    def create_superuser(self, first_name, last_name, phone_number, email, password = None):
        user = self.create_user(
            email = self.normalize_email(email),
            password = password,
            first_name = first_name,
            last_name = last_name,
            phone_number = phone_number
        )
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using = self._db)
        return user

class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=50, unique=True)
    
    # required
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superadmin = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [ 'first_name', 'last_name', 'phone_number']
    
    objects = MyAccountManager()
    
    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj = None):
        return self.is_superadmin
    
    def has_module_perms(self, add_label):
        return True


class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete = models.CASCADE, related_name = 'user_profile')
    otp = models.CharField(max_length = 6)
    uid = models.UUIDField(default=uuid.uuid4)

    def __str__(self):
        return self.otp
    
    
    
    
    
class AddressBook(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=20)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50,blank=True,null=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    pincode = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if self.is_default:
            # Set is_default=False for other addresses of the same user
            print(self.pk)
            AddressBook.objects.filter(user=self.user).exclude(pk=self.pk).update(is_default=False)
        super(AddressBook, self).save(*args, **kwargs)
        
    def get_user_full_address(self):
        address_parts = [self.name, self.phone,self.address_line_1]

        if self.address_line_2:
            address_parts.append(self.address_line_2)
        
        address_parts.append(f'<b>Pin: {self.pincode}</b>')
        address_parts.extend([self.city, self.state, self.country])
        
        
        return ', '.join(address_parts)
        # return f'{self.name},{self.phone},Pin:{self.pincode},Address:{self.address_line_1},{self.address_line_2},{self.city},{self.state},{self.country}'
    def __str__(self):
        return self.name
    