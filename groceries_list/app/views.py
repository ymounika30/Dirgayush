from django.views.generic import View, TemplateView, CreateView, FormView, DetailView, ListView,RedirectView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect,HttpResponseRedirect,HttpResponse,get_object_or_404
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import *
from . forms import *
from django.http import JsonResponse
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from rest_framework.exceptions import ValidationError
from rest_framework import generics, viewsets, status
from .serializers import *
from django.core import serializers
from rest_framework.viewsets import ModelViewSet
from app.serializers import ReviewSerializer
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.exceptions import AuthenticationFailed

@api_view(['GET','POST'])

def allproductapiall(request):

    if request.method=='GET':

        movies=Product.objects.all()

        serializer=productserializer(movies,many=True)

        return Response(serializer.data)

    if request.method=='POST':

        serializer=productserializer(data=request.data)

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        else:

            return Response(serializer.errors)

#user and admin login api view
class loginView(APIView):
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        print(username,password)
       
        user = User.objects.filter(username=username).first()
        
        user.set_password(password)
        if user is not None:
            if user.check_password(password):
                
                login(request, user)
                return Response({
                        'status': 'success',
                        'data': {'user': username},
                        'is_superuser': user.is_superuser,               
                        'message': 'login successful'
                    })
            else:
                raise AuthenticationFailed('Incorrect Password')
        else:
            raise AuthenticationFailed('user not found')


class ReviewCreate(generics.CreateAPIView):
    serializer_class=ReviewSerializer
    
    
    def get_queryset(self):
        return ContactModel.objects.all()
    
    def perform_create(self,serializer):
        pk=self.kwargs.get('pk')
        products=Product.objects.get(pk=pk)
        
        review_user=self.request.user
        review_queryset=ContactModel.objects.filter(product=products,review_user=review_user)
        
        if review_queryset.exists():
            raise ValidationError("You have reviewd this product!!!")
        
        if products.number_rating==0:
            products.avg_rating=serializer.validated_data['rating']
        else:
            products.avg_rating=(products.avg_rating+serializer.validated_data['rating'])/2
        products.number_rating=products.number_rating+1
        products.save()    
        serializer.save(watchlist=products,review_user=review_user)


class EcomMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer = request.user.customer
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)


class HomeView(EcomMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['myname'] = "tarak"
        all_products = Product.objects.all().order_by("category_id")
        paginator = Paginator(all_products, 8)
        page_number = self.request.GET.get('page')
        print(page_number)
        product_list = paginator.get_page(page_number)
        context['product_list'] = product_list
        return context


class AllProductsView(EcomMixin, TemplateView):
    template_name = "allproducts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategories'] = Category.objects.all()
        return context
        
        #all category list view
class AllcategoryView(EcomMixin, TemplateView):
    template_name = "admincategorylist.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategorylist'] = Category.objects.all()
        return context
#----
class ProductDetailView(EcomMixin, TemplateView):
    template_name = "productdetail.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_sku = self.kwargs['sku']
        product = Product.objects.get(sku=url_sku)
        us = ContactModel.objects.all()
        product.save()
        
        context = {'product':product, 'us':us}
 
        return context
        
class productviewset(viewsets.ModelViewSet):
    queryset=Product.objects.all()
    serializer_class=productserializer

class AddToCartView(EcomMixin, TemplateView):
    template_name = "addtocart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get product id from requested url
        product_id = self.kwargs['pro_id']
        # get product
        product_obj = Product.objects.get(id=product_id)

        # check if cart exists
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            this_product_in_cart = cart_obj.cartproduct_set.filter(
                product=product_obj)

            # item already exists in cart
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.selling_price
                cartproduct.save()
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
            # new item is added in cart
            else:
                cartproduct = CartProduct.objects.create(
                    cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price)
                cart_obj.total += product_obj.selling_price
                cart_obj.save()

        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct = CartProduct.objects.create(
                cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price)
            cart_obj.total += product_obj.selling_price
            cart_obj.save()

        return context


#manage cart ciew serilization

def manage_cart(request,cp_id):

    cart_product=CartProduct.objects.filter(id=cp_id)

    cart_pro_details=[]

    for i in cart_product:

        cart_pro_details.append(i)

    print(cart_pro_details)

    json_data=serializers.serialize('json',cart_pro_details)

    print(json_data)

    return HttpResponse(json_data)
class ManageCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cp_id = self.kwargs["cp_id"]
        action = request.GET.get("action")
        
        cp_obj = CartProduct.objects.get(id=cp_id)
       
        all = Product.objects.all()
        
        cart_obj = cp_obj.cart

        if action == "inc":
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()
        elif action == "dcr":
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()

        elif action == "rmv":
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        print("1st line")
        for i in all:
            
            if str(cp_obj.product)==str(i.title):
                a=i.quantity
                b=cp_obj.quantity
                c = a-b
                
                a = Product.objects.get(quantity=i.quantity)
                
                a.quantity=(c)
                
                a.save(update_fields=['quantity'])
                
        return redirect("app:mycart")


class EmptyCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total = 0
            cart.save()
        return redirect("app:mycart")


class MyCartView(EcomMixin, TemplateView):
    template_name = "mycart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        print(cart_id,'gdfhrh')
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart
        return context


class CheckoutView(EcomMixin, CreateView):
    template_name = "checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("app:pay")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect("/login/?next=/checkout/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None
        context['cart'] = cart_obj
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = "Order Received"
            del self.request.session['cart_id']
            pm = form.cleaned_data.get("payment_method")
            order = form.save()
            if pm == "razorpay":
                return redirect(reverse("app:razorpay") + "?o_id=" + str(order.id))
        else:
            return redirect("app:pay")
        return super().form_valid(form)
 
def razorpay(request):
    if request.method == 'POST':
        amount  = 50000
        order_currency = 'INR'
        client = razorpay.Client(auth=('rzp_test_tx5GNwIVukb1M5', 'u1VFiRHXTvfA4mgreg6tx01c'))
        payment = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': '1'})
    return render(request,'pay.html')


@csrf_exempt
def success(request):
    return render(request,'success.html') 

class CustomerRegistrationView(CreateView):
    template_name = "customerregistration.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("app:home")

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        user = User.objects.create_user(username, email, password)
        form.instance.user = user
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url
    
class Customerapiview(APIView):
    def post(self,request):
        data = request.data
        print(data)
        serializer=Customerserializer(data=data)  
        serializer.is_valid(raise_exception=True)
        serializer.save()
       
        print(serializer.data)
        id=serializer.data.get('id')
        first_name=serializer.data.get('first_name')
        user = User.objects.get(pk=id)
        print(user)
        add=Customer.objects.create(user=user,full_name=first_name)
        return Response(serializer.data)

    def get(self,request):
        user = User.objects.all()
        serializer =Customerserializer(user, many=True)
        return Response(serializer.data)

class CustomerLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("app:home")

#admin logout
class adminLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("app:home")


class CustomerLoginView(FormView):
    template_name = "customerlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("app:home")

class AboutView(EcomMixin, TemplateView):
    template_name = "about.html"


def contact(request):
    if request.user.is_authenticated:       
        if request.method == 'POST':
            fm = Contact(request.POST)
            if fm.is_valid():
                fm.save()
                messages.success(request,'Thanks for Contacting Us')
                return HttpResponseRedirect("/")
        else:
            fm = Contact()
        return render(request,'contact.html',{'form':fm})
    else:
        return HttpResponseRedirect('/')
    


class CustomerProfileView(TemplateView):
    template_name = "customerprofile.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context['customer'] = customer
        orders = Order.objects.filter(cart__customer=customer).order_by("-id")
        context["orders"] = orders
        return context


class CustomerOrderDetailView(DetailView):
    template_name = "customerorderdetail.html"
    model = Order
    context_object_name = "ord_obj"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            order_id = self.kwargs["pk"]
            order = Order.objects.get(id=order_id)
            if request.user.customer != order.cart.customer:
                return redirect("app:customerprofile")
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)



# admin pages
class AdminLoginView(FormView):
    template_name = "adminlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("app:adminhome")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)
        if usr is not None and Admin.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})
        return super().form_valid(form)
#adminlogin view serlization

class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/admin-login/")
        return super().dispatch(request, *args, **kwargs)


class AdminHomeView(AdminRequiredMixin, TemplateView):
    template_name = "adminhome.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pendingorders"] = Order.objects.filter(
            order_status="Order Received").order_by("-id")
        return context

#adminlogin view serlization

class AdminOrderDetailView(AdminRequiredMixin, DetailView):
    template_name = "adminorderdetail.html"
    model = Order
    context_object_name = "ord_obj"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allstatus"] = ORDER_STATUS
        return context


#admin feedback product details view serializers
def AdminOrderfeedbackDetailView(request):
    allproducts=ContactModel.objects.all()
    user_product=[]
    for i in allproducts:
        user_product.append(i)
    print(user_product)
    qs_json = serializers.serialize('json', user_product)
    print(qs_json)
    return HttpResponse(qs_json)


#admin order list view serializers
def AdminOrderListView(request):
    allproducts=Order.objects.all()
    user_product=[]
    for i in allproducts:
        user_product.append(i)
    
    qs_json = serializers.serialize('json', user_product)
    
    return HttpResponse(qs_json)


class AdminOrderStatuChangeView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs["pk"]
        order_obj = Order.objects.get(id=order_id)
        new_status = request.POST.get("status")
        order_obj.order_status = new_status
        order_obj.save()
        return redirect(reverse_lazy("app:adminorderdetail", kwargs={"pk": order_id}))


class AdminProductListView(AdminRequiredMixin, ListView):
    template_name = "adminproductlist.html"
    queryset = Product.objects.all().order_by("-id")
    context_object_name = "allproducts"

# new delete
def userListView(request):  
    return render(request,'userdelete.html')
    


# class AdminProductCreateView(AdminRequiredMixin, CreateView):
#     template_name = "adminproductcreate.html"
#     form_class = ProductForm
#     success_url = reverse_lazy("app:adminproductlist")

def image(request):
    if request.method == 'POST':
        print('inside posr')
        form=ProductForm(request.POST,request.FILES)
        # Get the uploaded image
        # image1 = request.FILES['image']

        # # Encode the image as base64
        
        if form.is_valid:
            print('inside valif')
            # Save the encoded image to the mode
            form.save()
            model = Product.objects.all().last()
            print(model.image)
            image1 = model.image

            image_file = image1.open()
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            # model = Product(**form.data,image=form.files['image'])
            # # image_model = Product(image=encoded_string)
            model.image = encoded_string
            # print('kkkkk')
            model.save()
        print('outside valif')
    else:
        form=ProductForm
    #print('outside else')
    return render(request,'adminproductcreate.html',{'form':form})

    # def form_valid(self, form):
    #     p = form.save()
    #     # images = self.request.FILES.getlist("more_images")
    #     # for i in images:
    #     #     ProductImage.objects.create(product=p, image=i)
    #     return super().form_valid(form)



        #admin category create
class admincategorycreate(AdminRequiredMixin, CreateView):
    template_name = "admincategorycreate.html"
    form_class = categoryform
    success_url = reverse_lazy("app:admincategorylist")

    

class DeleteView(RedirectView):
    url='/'
    def get_redirect_url(self,*args,**kwargs):
        del_id=kwargs['id']
        
        Product.objects.get(pk=del_id).delete()
        return super().get_redirect_url(*args,**kwargs)

class DeletecustomerView(RedirectView):
    url='/'
    def get_redirect_url(self,*args,**kwargs):
        
        del_id=kwargs['id']
        
        g=del_id
        print(g)
        a=Customer.objects.all()
        for i in a:
            if i.id==g:
                Customer.objects.get(id=i.id).delete()
                print('hi')
        return super().get_redirect_url(*args,**kwargs)  

class DeleteUserView(RedirectView):
    url='/'
    def get_redirect_url(self,*args,**kwargs):
        del_id=kwargs['id']
        
        Customer.objects.get(pk=del_id).delete()
        return super().get_redirect_url(*args,**kwargs)

def adminfeedback(request):
    fm = ContactModel.objects.all()
    
    return render(request,'adminfeedback.html',{'form':fm})

# admin feedback in serlizers
def adminfeedback(request):
    allproducts=ContactModel.objects.all()
    
    user_product=[]
    for i in allproducts:
        user_product.append(i)
    
    qs_json = serializers.serialize('json', user_product)
    
    return HttpResponse(qs_json)



class AdminUserListView(AdminRequiredMixin, ListView):
    template_name = "adminuserlist.html"
    queryset = Customer.objects.all().order_by("-id")
    context_object_name = "allusers"

def update_data(request, id):
    if request.method == 'POST':
        pi = Product.objects.get(pk=id)
        fm = ProductForm(request.POST, instance=pi)
        if fm.is_valid():
            fm.save()
    else:
        pi = Product.objects.get(pk=id)
        fm = ProductForm(instance=pi)
    return render(request, 'edit.html', {'form':fm})

    
class home(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        # Add image URLs to the serialized data
        data = serializer.data
        for item in data:
            item['image'] = request.build_absolute_uri(item['image'])
        return Response(data)


@api_view(['GET','POST'])
def stockapi(request):
    if request.method=='GET':
        movies=Stock.objects.all()
        serializer=stockSerializer(movies,many=True)
        return Response(serializer.data)
    if request.method=='POST':
        serializer=stockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


@api_view(['GET','POST'])
def categoryapi(request):
    if request.method=='GET':
        movies=Category.objects.all()
        serializer=CategorySerializer(movies,many=True)
        return Response(serializer.data)
    if request.method=='POST':
        serializer=CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

@api_view(['GET','POST','PUT','DELETE'])
def product_detail(request,id):
    if request.method=='GET':
        try:
            movie=Product.objects.get(pk=id)
        except Product.DoesNotExist:
            return Response({'Error':'Data not found'},status=status.HTTP_404_NOT_FOUND)
        serializer=ProductSerializer(movie)
        return Response(serializer.data)
    if request.method=='POST':
        serializer=ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
    if request.method=='PUT':
        movie=Product.objects.get(pk=id)
        serializer=ProductSerializer(movie,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    if request.method=='DELETE':
        movie=Product.objects.get(pk=id)
        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




@api_view(['GET','POST'])
def contact(request):
    if request.method=='GET':
        movies=ContactModel.objects.all()
        serializer=ContactSerializer(movies,many=True)
        return Response(serializer.data)
    if request.method=='POST':
        serializer=ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

@api_view(['GET'])
def profile(request):
    if request.method=='GET':
        movies=Customer.objects.all()
        serializer=Customerserializer(movies,many=True)
        return Response(serializer.data)
    
@api_view(['GET','POST'])
def order(request):
    if request.method=='GET':
        movies=Order.objects.all()
        serializer=OrderSerializer(movies,many=True)
        return Response(serializer.data)
    if request.method=='POST':
        serializer=OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


#admin user details 
@api_view(['GET','DELETE'])
def customerinfo(request,pro_id):
    if request.method=='GET':
        try:
            user=Customer.objects.get(pk=pro_id)
        except Customer.DoesNotExist:
            return Response({'Error':'Customer not found'},status=status.HTTP_404_NOT_FOUND)
        serializer=customerSerializer(user)
        return Response(serializer.data)
    
    if request.method=='DELETE':
        movie=Customer.objects.get(pk=pro_id)
        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#admin order details

@api_view(['GET'])
def displayorder(request):
    if request.method=='GET':
        movies=Order.objects.all()
        serializer=OrderSerializer(movies,many=True)
        return Response(serializer.data)


#admin user list view
def adminuserlist(request):

    allproducts=Customer.objects.all().order_by("-id")
    
    user_product=[]
    for i in allproducts:
        user_product.append(i)
    
    qs_json = serializers.serialize('json', user_product)
    
    return HttpResponse(qs_json)

@api_view(['GET'])
def adminuserdisplay(request):
    if request.method=='GET':
        user=Customer.objects.all()
        serializer=customerSerializer(user,many=True)
        return Response(serializer.data)


# @api_view(['DELETE'])
# def adminuserdelete(request,pro_id):
#     if request.method=='DELETE':
#         user=Customer.objects.get(pk=pro_id)
#         user.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
# 



class ProductListcreatepost(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        # Add image URLs to the serialized data
        data = serializer.data
        for item in data:
            item['image'] = request.build_absolute_uri(item['image'])
        return Response(data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Save the product with the image
        product = serializer.save()
        product.image = request.build_absolute_uri(product.image.url)
        product.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class ProductDetailupdatedelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        serializer.data['image'] = request.build_absolute_uri(serializer.data['image'])
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        # Save the product with the image
        product = serializer.save()
        product.image = request.build_absolute_uri(product.image.url)
        product.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

# 
@api_view(['GET','POST'])
def adminproductapicr(request):
    if request.method=='GET':
        movies=Product.objects.all()
        serializer=ProductSerializer(movies,many=True)
        return Response(serializer.data)
    if request.method=='POST':
        serializer=ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
            

@api_view(['GET','PUT','DELETE'])
def adminproductud(request,pro_id):
    if request.method=='GET':
        try:
            detail=Product.objects.get(pk=pro_id)
        except Product.DoesNotExist:
            return Response({'Error':'Data not found'},status=status.HTTP_404_NOT_FOUND)
        serializer=ProductSerializer(detail)
        return Response(serializer.data)
    if request.method=='PUT':
        detail=Product.objects.get(pk=pro_id)
        serializer=ProductSerializer(detail,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    if request.method=='DELETE':
        movie=Cart.objects.get(pk=pro_id)
        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
# 
@api_view(['GET','POST'])
def adminfeedbackdisplay(request):
    if request.method=='GET':
        feedback=ContactModel.objects.all()
        serializer=feedbackSerializer(feedback,many=True)
        return Response(serializer.data)
    if request.method=='POST':
        serializer=feedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response('logged out succefully')

@api_view(['GET','POST'])
def manage_cart(request):
    if request.method=='GET':
        movies=CartProduct.objects.all()
        serializer=CartProductSerializer(movies,many=True)
        return Response(serializer.data)
    if request.method=='POST':
        serializer=CartProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


@api_view(['GET','PUT','DELETE'])
def add_cart(request,pro_id):
    if request.method=='GET':
        try:
            movie=Cart.objects.get(pk=pro_id)
        except Cart.DoesNotExist:
            return Response({'Error':'Data not found'},status=status.HTTP_404_NOT_FOUND)
        serializer=CartSerializer(movie)
        return Response(serializer.data)
    if request.method=='PUT':
        movie=Cart.objects.get(pk=pro_id)
        serializer=CartSerializer(movie,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    if request.method=='DELETE':
        movie=Cart.objects.get(pk=pro_id)
        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET','POST','PUT','DELETE'])
def managecart(request,id):
    if request.method=='GET':
        movies=CartProduct.objects.all()
        serializer=CartProductSerializer(movies,many=True)
        return Response(serializer.data)
    if request.method=='POST':
        serializer=CartProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
    if request.method=='PUT':
        movie=Cart.objects.get(pk=id)
        serializer=CartProductSerializer(movie,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    if request.method=='DELETE':
        movie=CartProduct.objects.get(pk=id)
        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# class IncrementCartProductView(APIView):
#     def post(self, request, product_id):
#         product = CartProduct.objects.get(id=product_id)
#         product.price += request.data.get('price', 0)
#         product.quantity += request.data.get('quantity', 0)
#         product.save()
#         serializer = CartProductSerializer(product)
#         return Response(serializer.data)



# class Productapi(ModelViewSet):
#     queryset = Product.objects.all()
#     serializer_class = productserializer1
