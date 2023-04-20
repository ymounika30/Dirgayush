from django import forms
from .models import *
from django.contrib.auth.models import User

weights =(
    ("1", "One"),
    ("2", "Two"),
    ("3", "Three"),
    ("4", "Four"),
    ("5", "Five"),
)
class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["ordered_to", "shipping_address",
                  "mobile", "email", "payment_method"]


class CustomerRegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.CharField(widget=forms.EmailInput())
    
    class Meta:
        model = Customer
        fields = ["username", "password", "email", "full_name", "address"]

    def clean_username(self):
        uname = self.cleaned_data.get("username")
        
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError(
                "Customer with this username already exists.")
        

        return uname
    
    def clean_email(self):
        
        em = self.cleaned_data.get("email")
        if User.objects.filter(email=em).exists():
            raise forms.ValidationError(
                "Customer with this email already exists."
            )
        

        return em


class CustomerLoginForm(forms.Form):
     # username = forms.CharField(widget=forms.TextInput())
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())



class ProductForm(forms.ModelForm):
    more_images = forms.FileField(required=False, widget=forms.FileInput(attrs={
        "class": "form-control",
        "multiple": True
    }))

    class Meta:
        model = Product
        fields = ["title","stock","category", "image", "marked_price",
                  "selling_price","quantity","type_of_quantity","description"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter the product title here..."
            }),
            "stock": forms.Select(attrs={
                "class": "form-control"
            }),
           
            "category": forms.Select(attrs={
                "class": "form-control"
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
            "marked_price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Marked price of the product..."
            }),
            "selling_price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Selling price of the product..."
            }),
             "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "quantity of the product..."
            }),
             "types_of_weights": forms.ChoiceField(choices = weights
                
            ),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Description of the product...",
                "rows": 5
            }),

        }

    

class categoryform(forms.ModelForm):
    

    class Meta:
        model = Category
        fields = ["title"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter the product title here..."
            }),
            
           

        }
    

    
        
class Contact(forms.ModelForm):
    class Meta:
        model = ContactModel
        fields= '__all__'


