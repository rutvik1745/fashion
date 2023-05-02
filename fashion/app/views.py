from django.shortcuts import render,redirect
from django.views import View
from .forms import  CustmoerProfileForm
from .models import Customer, Product, Cart, Order, Category, SubCategory
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from .models import *
import uuid
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
import re


def login_attempt(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username = username).first()
        if user_obj is None:
            messages.success(request, 'User not found.')
            return redirect('/login')
        
        customer_obj = Customer.objects.filter(user = user_obj ).first()

        if not customer_obj.is_verified:
            messages.success(request, 'Profile is not verified check your mail.')
            return redirect('/login')

        user = authenticate(username = username , password = password)
        if user is None:
            messages.success(request, 'Wrong password.')
            return redirect('/login')
        
        login(request, user)
        return redirect('/')

    return render(request , 'app/login.html')

def register_attempt(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
            return redirect('/customerregistration')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already taken.')
            return redirect('/customerregistration')

     
        if len(password) < 8:
            messages.success(request, 'Password must be at least 8 characters long.')
            return redirect('/customerregistration')

        if not re.search("[a-z]", password):
            messages.success(request, 'Password must contain at least one lowercase letter.')
            return redirect('/customerregistration')

        if not re.search("[A-Z]", password):
            messages.success(request, 'Password must contain at least one uppercase letter.')
            return redirect('/customerregistration')

        if not re.search("[0-9]", password):
            messages.success(request, 'Password must contain at least one digit.')
            return redirect('/customerregistration')

        if not re.search("[!@#$%^&*(),.?\":{}|<>]", password):
            messages.success(request, 'Password must contain at least one special character.')
            return redirect('/customerregistration')

        try:
            user_obj = User.objects.create_user(username=username, email=email, password=password)
            auth_token = str(uuid.uuid4())
            customer_obj = Customer.objects.create(user=user_obj, auth_token=auth_token)
            send_mail_after_registration(email, auth_token)
            return redirect('/token')
        except Exception as e:
            print(e)

    return render(request, 'app/customerregistration.html')



def token_send(request):
    return render(request , 'app/token_send.html')

def verify(request , auth_token):
    try:
        customer_obj = Customer.objects.filter(auth_token = auth_token).first()
    
        if customer_obj:
            if customer_obj.is_verified:
                messages.success(request, 'Your account is already verified.')
                return redirect('/app/login')
            customer_obj.is_verified = True
            customer_obj.save()
            messages.success(request, 'Your account has been verified.')
            return redirect('/login')
        else:
            return redirect('/error')
    except Exception as e:
        return redirect('/')

def error_page(request):
    return  render(request , 'app/error.html')

def send_mail_after_registration(email , token):
    subject = 'Your accounts need to be verified'
    message = f'Hi paste the link to verify your account http://127.0.0.1:8000/verify/{token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message , email_from ,recipient_list )

class ProductView(View):
     def get(self, request):
        search_text = request.GET.get('search_text', '')
        products = Product.objects.filter(Q(name__icontains=search_text) | Q(description__icontains=search_text))
        men = Product.objects.filter(category=1)
        women = Product.objects.filter(category=2)
        kids = Product.objects.filter(category=3)

        return render(request, 'app/home.html', {'product': products, 'men': men, 'women': women, 'kids': kids})
        
class ProductDetailView(View):
 def get(self, request, pk):
    product= Product.objects.get(pk=pk)
    return render(request, 'app/productdetail.html',
    {'product':product})
 
def search(request):
    query = request.GET.get('q')
    # print(query)
    if query:
        products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(brand__icontains=query))
    else:
        products = Product.objects.all()
    
    return render(request, 'app/shop.html', {'productList': products})

 
class ShopProductView(View):
    def get(self, request):
        productList = Product.objects.all()
        categories = Category.objects.all()
        return render(request, 'app/shop.html',
        {'productList':productList,'categories':categories}) 
     
def getSubCategories(request,id):
  categories = Category.objects.all()
  category=Category.objects.get(id=id)
  request.session['categoryId_session']=category.id
  productList=Product.objects.filter(category=category)
  subCategories=[]
  for productCategory in productList:
    print("  ",productCategory.name)
    if productCategory.subcategory not in subCategories:
      subCategories.append(productCategory.subcategory)
  

  return render(request, 'app/shop.html',
        {'categories':categories,'subCategories':subCategories,'productList':productList}) 

def getProducts(request, id):
    categories = Category.objects.all()
    category = Category.objects.get(id=request.session.get('categoryId_session'))
    findSubCategories = Product.objects.filter(category=category)
    subCategories = []
    for subCat in findSubCategories:
        if subCat.subcategory not in subCategories:
            subCategories.append(subCat.subcategory)

    subcategory = SubCategory.objects.get(id=id)
    productList = Product.objects.filter(category=category, subcategory=subcategory)

    return render(request, 'app/shop.html',
                  {'categories': categories, 'subCategories': subCategories, 'productList': productList})


def add_to_cart(request): 
 user=request.user
 product_id= request.GET.get('prod_id')
 product = Product.objects.get(id=product_id)
 try:
   cart=Cart.objects.get(user=user,product=product)
 except:
    Cart(user=user, product=product).save()
 return redirect('/cart')


def show_cart(request):
   if request.user.is_authenticated:
     user = request.user
     cart = Cart.objects.filter(user=user)
     amount = 0
     shipping_amount = 70
     total_amount = 0
     cart_product = [p for p in  Cart.objects.all() if p.user ==
      user]
     if cart_product:
       for p in cart_product:
         tempamount = (p.quantity*p.product.discounted_price)
         amount += tempamount
         totalamount = amount + shipping_amount
       return render(request, 'app/addtocart.html',
        {'carts':cart,'totalamount':totalamount,'amount':amount})
     else:
       return render(request, 'app/emptycart.html')
 
def plus_cart(request):
  if request.method =='GET':
    prod_id = request.GET['prod_id']
    c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
    c.quantity+=1
    c.save()
    amount = 0
    shipping_amount = 70
    cart_product = [p for p in  Cart.objects.all() if p.user == request.user]
    for p in cart_product:
      tempamount = (p.quantity*p.product.discounted_price)
      amount += tempamount
      

    data= {
        'quantity': c.quantity,
        'amount':amount,
        'totalamount':amount + shipping_amount
      }
    return JsonResponse(data)

def minus_cart(request):
  if request.method =='GET':
    prod_id = request.GET['prod_id']
    c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
    c.quantity-=1
    c.save()
    amount = 0
    shipping_amount = 70
    cart_product = [p for p in  Cart.objects.all() if p.user == request.user]
    for p in cart_product:
      tempamount = (p.quantity*p.product.discounted_price)
      amount += tempamount
     

    data= {
        'quantity': c.quantity,
        'amount':amount,
        'totalamount':amount  + shipping_amount
      }
    return JsonResponse(data)

def remove_cart(request):
  if request.method =='GET':
    prod_id = request.GET['prod_id']
    c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
    c.delete()
    amount = 0
    shipping_amount = 70
    cart_product = [p for p in  Cart.objects.all() if p.user == request.user]
    for p in cart_product:
      tempamount = (p.quantity*p.product.discounted_price)
      amount += tempamount
     

    data= {
      
        'amount':amount,
        'totalamount':amount + shipping_amount
      }
    return JsonResponse(data)


def buy_now(request):
 return render(request, 'app/buynow.html')

def address(request):
 add = Customer.objects.filter(user=request.user)
 return render(request, 'app/address.html',{'add':add,  
 'active':'btn-primary'})



class ProfileView(View):
    def get(self, request):
        user = request.user
        if hasattr(user, 'customer'):
            customer = user.customer
            form = CustmoerProfileForm(instance=customer)
        else:
            form = CustmoerProfileForm()
            customer = None

        return render(request, 'app/profile.html', {'form': form, 'customer': customer, 'active': 'btn-primary'})

 
    def post(self, request):
        form = CustmoerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            mobile = form.cleaned_data['mobile']
            address = form.cleaned_data['address']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            
            if hasattr(user, 'customer'):
                customer = user.customer
            else:
                customer = Customer(user=user)
            
            customer.name = name
            customer.mobile = mobile
            customer.address = address
            customer.city = city
            customer.state = state
            customer.zipcode = zipcode
            customer.save()
            return redirect('/address')  # Redirect the user to the address page if they don't have a Customer object

        else:
            user = request.user
            if hasattr(user, 'customer'):
                customer = user.customer
            else:
                customer = None
        
        form = CustmoerProfileForm(instance=customer)
        
        return render(request, 'app/profile.html', {'form': form, 'customer': customer, 'active': 'btn-primary'})


def payment_done(request):
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    order = Order.objects.create(user=user, customer=customer)  # create a new order
    for c in cart:
        ExtendOrder(order=order, product=c.product, quantity=c.quantity).save()  # associate the order with ExtendOrder
        c.delete()
    return redirect("orders")


def orders(request):
    op = Order.objects.filter(user=request.user)
    dict = {}
    list = []

    for i in op:
        ex_op = ExtendOrder.objects.filter(order=i.id)
        dict[i.id] = ex_op
    for y in dict.values():
        list.append(y)

    if not op:
        message = "You haven't placed any orders yet."
        return render(request, 'app/orders.html', {'message': message})

    for x in list:
        for i in x:
            return render(request, 'app/orders.html', {'order_placed': op, 'list': list})


def cancel_order(request, order_id):
    order = Order.objects.get(id=order_id)
    print(order_id)
    
    # Only allow cancellation if the order status is still 'Pending'
    if order.status == 'Pending':
        order.status = 'Cancel'
        order.save()
        order.delete()
        messages.success(request, 'Order cancelled successfully.')
    else:
        messages.error(request, 'Sorry, you cannot cancel this order as it has already been accepted.')
    
    return redirect('orders')



def checkout(request):
 user= request.user
 add = Customer.objects.filter(user=user)
 cart_items = Cart.objects.filter(user=user)
 amount = 0.0
 shipping_amount = 70.0
 totalamount = 0.0
 cart_product = [p for p in  Cart.objects.all() if p.user == request.user]
 if cart_product:
    for p in cart_product:
      tempamount = (p.quantity*p.product.discounted_price)
      amount += tempamount
    totalamount= amount + shipping_amount
 return render(request, 'app/checkout.html',{'add':add, 'totalamount':totalamount,'cart_items':cart_items})