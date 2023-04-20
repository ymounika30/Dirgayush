from django.urls import path,include
from . import views
# from rest_framework import routers

# router=routers.DefaultRouter()
# # # router.register("signupapi",views.Customerapiview, basename='signupapi'),
# # router.register("adminproductapi/",views.adminproductapi.as_view, basename='ff'),
# router.register("productapi", views.Productapi, basename="Productapi"),






app_name = "app"

urlpatterns = [

    # User pages
    path('allproductapiall/',views.allproductapiall,name='allproductapiall'),
   
    # path("adminproduct/",views.adminproductapi.as_view(), name='adminproduct'),
    # path("ap/",include(router.urls)),
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("contact/", views.contact, name="contact"),
    path("all-products/", views.AllProductsView.as_view(), name="allproducts"),
    path("product/<slug:slug>/", views.ProductDetailView.as_view(), name="productdetail"),
    path("add-to-cart-<int:pro_id>/", views.AddToCartView.as_view(), name="addtocart"),
    path("my-cart/", views.MyCartView.as_view(), name="mycart"),
    path("manage-cart/<int:cp_id>/", views.ManageCartView.as_view(), name="managecart"),
    path("manage-cart/<int:cp_id>/", views.manage_cart, name="managecart"),

    path("empty-cart/", views.EmptyCartView.as_view(), name="emptycart"),
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("register/",views.CustomerRegistrationView.as_view(), name="customerregistration"),
    # path('registerview/',views.registerview,name='registerview'),
    path("logout/", views.CustomerLogoutView.as_view(), name="customerlogout"),

    path("login/", views.CustomerLoginView.as_view(), name="customerlogin"),
    path("profile/", views.CustomerProfileView.as_view(), name="customerprofile"),
    path("profile/order-<int:pk>/", views.CustomerOrderDetailView.as_view(),name="customerorderdetail"),
    #path("search/", views.SearchView.as_view(), name="search"),
    path('pay/',views.razorpay,name='pay'),
    
    path('pay/success',views.success,name='success'),
    # Admin pages
    path("admin-login/", views.AdminLoginView.as_view(), name="adminlogin"),
    path("admin-home/", views.AdminHomeView.as_view(), name="adminhome"),
    path("admin-order/<int:pk>/", views.AdminOrderDetailView.as_view(),name="adminorderdetail"),
    path("admin-all-orders/", views.AdminOrderListView, name="adminorderlist"),
    # path("admin-all-orders/", views.AdminOrderListView.as_view(), name="adminorderlist"),AdminOrderListView,
    path("admin-order-<int:pk>-change/",views.AdminOrderStatuChangeView.as_view(), name="adminorderstatuschange"),
    path("admin-product/list/", views.AdminProductListView.as_view(),name="adminproductlist"),
    path("admin-users/list/", views.AdminUserListView.as_view(),name="adminuserlist"),
    # path("admin-product/add/", views.AdminProductCreateView.as_view(),name="adminproductcreate"),
    path("admin-product/add/", views.image,name="adminproductcreate"),
    path('edit/<int:id>/', views.update_data,name='edit'),
    path('delete/<int:id>/', views.DeleteView.as_view(),name='delete'),
    path('userdelete/<int:id>/', views.DeleteUserView.as_view(),name='userdelete'),
    # path('userdelete/<int:id>/', views.DeleteUserView,name='userdelete'),
    path('userListView',views.userListView,name='userListView'),
    path('customerdelete/<int:id>/', views.DeletecustomerView.as_view(),name='customerdelete'),
    # path('customerdelete/<int:id>/', views.DeletecustomerView,name='customerdelete'),
    path('adminfeedback/',views.adminfeedback,name='adminfeedback'),
    path("admin-order/<int:pk>/", views.AdminOrderDetailView.as_view(),name="adminorderdetail"),
    # path("adminfeedbackorder/<int:pk>/", views.AdminOrderfeedbackDetailView.as_view(),name="adminorderfeedbackdetail"),
    path("adminfeedbackorder/", views.AdminOrderfeedbackDetailView,name="adminorderfeedbackdetail"),
    path("admincategorylist", views.AllcategoryView.as_view(),name="admincategorylist"),
    path('admincategorycreate/',views.admincategorycreate.as_view(),name='admincategorycreate'), 
    path("adminlogout/", views.adminLogoutView.as_view(), name="adminlogout"),


    #userapi urls
    path("api/", views.home.as_view(), name="home"),
    path("api/categoryapi/", views.categoryapi, name="categoryapi"),
    path("api/product/<int:id>/", views.product_detail, name="productdetail"),
    path("api/addtocart/<int:pro_id>/", views.add_cart, name="addtocart"),
    path('api/managecart/<int:id>/',views.managecart,name="managecart"),
    path("api/contact/", views.contact, name="contact"),
    path("api/profile/", views.profile, name="profile"),
    path("api/order/", views.order,name="customerorderdetail"),
    path("api/manage_cart/",views.manage_cart,name="manage_cartapi" ),
    #path('api/increment/<int:product_id>/',views.IncrementCartProductView.as_view(),name='incrementcartproduct'),

    
    # 
    path("api/customerinfo/<int:pro_id>/", views.customerinfo,name="customerinfo"),
    path("api/displayorder/", views.displayorder,name="displayorder"),
    path('loginapi/', views.loginView.as_view(), name='loginapi'),
    # 
    path('ProductDetailupdatedelete/<int:pk>/', views.ProductDetailupdatedelete.as_view(), name='ProductDetailupdatedelete'),
    path('ProductListcreatepost/', views.ProductListcreatepost.as_view(), name='ProductListcreatepost'),
    # 
    path("signupapi/",views.Customerapiview.as_view(), name='signupapi'),
    path("api/stockapi/", views.stockapi, name="stockapi"),
    path("api/adminuserdisplay/", views.adminuserdisplay, name="adminuserdisplay"),
   
    path("api/adminproductapicr/", views.adminproductapicr, name="adminproductapicr"),
    path("api/adminproductud/<int:pro_id>/", views.adminproductud, name="adminproductud"),
    path("api/adminfeedbackdisplay/", views.adminfeedbackdisplay, name="adminfeedbackdisplay"),
    path("api/LogoutView/", views.LogoutView.as_view(), name="LogoutView"),
    
    #Image Upload
    path('upload/', views.upload_image, name='upload_image'),


]
