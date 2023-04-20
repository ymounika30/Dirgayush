from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator,MinValueValidator
from cryptography.fernet import Fernet
import base64
# Create your models here.


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50)
    image = models.ImageField(upload_to="admins")
    mobile = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    address = models.CharField(max_length=200, null=True, blank=True)
    joined_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class Category(models.Model):
    title = models.CharField(max_length=200)
   
    def __str__(self):
        return self.title

class Stock(models.Model):
    title = models.CharField(max_length=200)
   
    def __str__(self):
        return self.title
    




types_of_weight = (
    ("kg", "kg"),
    ("pieces", "pieces"),
    ("liters", "liters"),
    ("grams", "grams"),
    
)
def upload_path(instance,filename):
    return '/'.join(['products',str(instance)])

# class Product(models.Model):
#     title = models.CharField(max_length=200)
#     stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     image = models.ImageField(upload_to="products")
#     image_data = models.BinaryField(null=False)
#     marked_price = models.PositiveIntegerField()
#     selling_price = models.PositiveIntegerField()
#     quantity = models.PositiveIntegerField()
#     date = models.DateTimeField(auto_now_add=True)
#     type_of_quantity = models.CharField(max_length=50, choices=types_of_weight)
#     description = models.TextField()
    
#     def __str__(self):
#         return self.title
#     def save(self, *args, **kwargs):
#         # Encrypt the binary data of the image file
#         if self.image:
#             key = Fernet.generate_key()
#             fernet = Fernet(key)
#             encrypted_data = fernet.encrypt(self.image.read())
#             self.image_data = encrypted_data
        
#         super().save(*args, **kwargs)
from django.conf import settings
from django.db import models
from django.utils.timezone import now
from urllib.parse import urljoin

class Product(models.Model):
    title = models.CharField(max_length=200)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products")
    marked_price = models.PositiveIntegerField()
    selling_price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    type_of_quantity = models.CharField(max_length=50, choices=types_of_weight)
    description = models.TextField()
    
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Save the image file to the file system
        super().save(*args, **kwargs)
        
        # Set the image_data field to the URL of the image file
        if self.image:
            self.image_data = urljoin(settings.MEDIA_URL, self.image.name)

        super().save(*args, **kwargs)


                  



class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/images/")

    def __str__(self):
        return self.product.title

class Cart(models.Model):
    customer = models.ForeignKey(
    Customer, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Cart: " + str(self.id)


# class CartProduct(models.Model):
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     rate = models.PositiveIntegerField()
#     quantity = models.PositiveIntegerField()
#     subtotal = models.PositiveIntegerField()

#     def __str__(self):
#         return "Cart: " + str(self.cart.id) + " CartProduct: " + str(self.id)


class CartProduct(models.Model):
    title=models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    quantity = models.IntegerField()
    # subtotal = models.PositiveIntegerField()

    def __str__(self):
        return "Cart: " + str(self.cart.id) + " CartProduct: " + str(self.id)


ORDER_STATUS = (
    ("Order Received", "Order Received"),
    ("Order Processing", "Order Processing"),
    ("On the way", "On the way"),
    ("Order Completed", "Order Completed"),
    ("Order Canceled", "Order Canceled"),
)

METHOD = (
    
    ("Razor Pay","Razor Pay"),
)


class Order(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    ordered_to = models.CharField(max_length=200)
    shipping_address = models.CharField(max_length=200)
    mobile = models.CharField(max_length=10)
    email = models.EmailField(null=True, blank=True)
    subtotal = models.PositiveIntegerField()
    discount = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(
        max_length=20, choices=METHOD, default="Razor Pay")
    payment_completed = models.BooleanField(
        default=False, null=True, blank=True)

    def __str__(self):
        return "Order: " + str(self.id)

class ContactModel(models.Model):
    orderid=models.ForeignKey(Order, on_delete=models.CASCADE,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    feedback = models.CharField(max_length=100,null=True)
    rating=models.PositiveIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)],null=True)

    
  
class Image(models.Model):
    image=models.TextField()