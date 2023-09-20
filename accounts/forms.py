from django import forms
from django.contrib.auth import get_user_model
from accounts.models import AddressBook
User = get_user_model()
class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
                'first_name',
                'last_name',
                'phone_number',
                'email',
                'is_superadmin',
                'is_staff',
                'is_active',
                ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            }
        

class SigninForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class AddressBookForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
    class Meta:
        model = AddressBook
        exclude = ('user','is_default','is_active')



class UserProfilePicForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_pic']