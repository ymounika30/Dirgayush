from rest_framework import serializers
from . models import *
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import User
from . forms import *
from django.contrib.auth import authenticate


#user serlizer



class ReviewSerializer(serializers.ModelSerializer):
    review_user=serializers.StringRelatedField(read_only=True)
    class Meta:
        model=ContactModel
        # fields="__all__"
        exclude=('products',)

class productserializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields='__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

# class ImageSerializer(serializers.ModelSerializer):
#     model=Product
#     fields=['image',]


class Customerserializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields= ['id','username', 'email', 'first_name','password']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    
    
class stockSerializer(serializers.ModelSerializer):
    class Meta:
        model=Stock
        fields='__all__'   


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields='__all__'

class ProductSerializer(serializers.ModelSerializer):
    stock = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    class Meta:
        model=Product
        fields='__all__'

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model=Cart
        fields='__all__'

class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=CartProduct
        fields='__all__'

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model=ContactModel
        fields='__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields=["ordered_by", "shipping_address",
                  "mobile", "email", "payment_method"]
class customerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Customer
        fields='__all__'

class feedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model=ContactModel
        fields=['orderid','feedback','rating']


    


# class productserializer1(serializers.ModelSerializer):
#     stock = serializers.CharField(source = 'stock.title', read_only=True)
#     category = serializers.CharField(source = 'category.title', read_only=True)

#     class Meta:
#         model=Product
#         fields='__all__'


   
#     def create(self, validated_data):
#         request = self.context.get('request')
#         stock = request.data.get('title')
#         stock = Stock.objects.get(title=stock)
#         validated_data['stock'] = stock

    
#         request = self.context.get('request')
#         category = request.data.get('category')
#         category = Category.objects.get(title=category)
#         validated_data['category'] = category

#         instance = self.Meta.model(**validated_data)        
#         instance.Stock = stock        
#         instance.Category = category               
#         instance.save()
 


class ProductSerializer(serializers.ModelSerializer):
    # image = serializers.ImageField(max_length=None, use_url=True)
    class Meta:
        model = Product
        fields = ['id', 'title', 'stock', 'category', 
                  'image', 'marked_price', 'selling_price', 
                  'quantity', 'date', 'type_of_quantity', 'description']

