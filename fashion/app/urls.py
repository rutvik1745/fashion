from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from .views import *
from app import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .forms import  MyPasswordChangeForm, MyPasswordResetForm, MySetPasswordForm
from .middlewares.auth import auth_middleware

admin.site.site_header ="fashion"
admin.site.site_title ="fashion"
admin.site.index_title="Welcome to fashion"

urlpatterns = [
    

     path('orders/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),

    path('error' , error_page , name="error"),


    path("", views.ProductView.as_view(), name="home"),
     path('search/', views.search, name='search'),

    path('customerregistration/' , register_attempt , name="customerregistration"),
    path('login/' , login_attempt , name="login"),
    path('token' , token_send , name="token_send"),
    path('verify/<auth_token>' , verify , name="verify"),
    path('error' , error_page , name="error"),
    path('product-detail/<int:pk>', views.ProductDetailView.
    as_view(), name='product-detail'),
    path('shop/',views.ShopProductView.as_view(),name='shop'),
    path('getSubCategories/<int:id>',views.getSubCategories,name='getSubCategories'),
    path('getProducts/<int:id>',views.getProducts,name='getProducts'),
    path('add-to-cart/',auth_middleware(views.add_to_cart), name='add-to-cart'),
    path('cart/', auth_middleware(views.show_cart),name='showcart'),
    path('pluscart/',auth_middleware( views.plus_cart)),
    path('minuscart/',auth_middleware( views.minus_cart)),
    path('removecart/',auth_middleware( views.remove_cart)),
    path('profile/', auth_middleware(views.ProfileView.as_view()), name='profile'),
    path('address/', auth_middleware(views.address), name='address'),
    path('orders/', auth_middleware(views.orders), name='orders'),
    path('logout/', auth_middleware(auth_views.LogoutView.as_view(next_page='login')),name='logout'),
    path('passwordchange/', auth_middleware(auth_views.PasswordChangeView
         .as_view(template_name='app/passwordchange.html',
         form_class=MyPasswordChangeForm,success_url='/passwordchangedone/')), name='passwordchange'),
    path('passwordchangedone/', auth_middleware(auth_views.PasswordChangeView.
         as_view(template_name='app/passwordchangedone.html')),
         name='passwordchangedone'),
    path('password-reset/', auth_views.PasswordResetView.
         as_view(template_name='app/password_reset.html',
          form_class=MyPasswordResetForm),name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.
         as_view(template_name='app/password_reset_done.html',
          ),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.
         as_view(template_name='app/password_reset_confirm.html',
          form_class=MySetPasswordForm),name='password_reset_confirm'),    
    path('password-reset-complete/',auth_views.PasswordResetCompleteView.
         as_view(template_name='app/password_reset_complete.html'),
          name='password_reset_complete'),
    path('checkout/',auth_middleware( views.checkout), name='checkout'),
    path('paymentdone/',auth_middleware( views.payment_done), name='paymentdone'),


] + static(settings.MEDIA_URL, document_root=settings.
MEDIA_ROOT)

