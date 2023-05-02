from django.db import models
from django.contrib.auth.models import User
# from django.core.validators import MaxValueValidator
# from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class Customer(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=100 )
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=25)
    city = models.CharField(max_length=20)
    zipcode = models.IntegerField(null=True)
    state = models.CharField(max_length=50)
    mobile = models.IntegerField(null=True)
    address = models.TextField(max_length=200)
    def __str__(self):
        return self.user.username


class Category(models.Model):
    cat_name = models.CharField(max_length=15)
    def __str__(self):
        return str(self.cat_name)
    

class SubCategory(models.Model):
    sub_cat_name = models.CharField(max_length=45)
    def __str__(self):
        return str(self.sub_cat_name)
   
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    selling_price = models.IntegerField()
    discounted_price = models.IntegerField()
    description = models.TextField(null=True)
    brand = models.CharField(max_length=25, default='')    
    image1 = models.ImageField(upload_to='producting',max_length=100)
    image2 = models.ImageField(upload_to='producting',max_length=100)
    image3 = models.ImageField(upload_to='producting',max_length=100)
    image4 = models.ImageField(upload_to='producting',max_length=100)
    def __str__(self):
        return str(self.id)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    def __str__(self):
        return str(self.id)
    
    @property
    def total_cost(self):
        return self.quantity *self.product.discounted_price

    

class Order(models.Model):
    STATUS_CHOICES = (
    ('Pending','Pending'),
    ('Accepted','Accepted'),
    ('Packed','Packed'),
    ('On The Way','On The Way'),
    ('Delivered','Delivered',),
    ('Cancel','Cancel'),
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50,choices=STATUS_CHOICES,default='Pending')
    def __str__(self):
        return str(self.id)
    def customer_name(self):
        return self.customer.name

    customer_name.short_description = 'name'
    def customer_city(self):
        return self.customer.city
    customer_city.short_description = 'city'

    def customer_address(self):
        return self.customer.address
    customer_address.short_description = 'address'

    def customer_zipcode(self):
        return self.customer.zipcode
    customer_zipcode.short_description = 'zipcode'

    def customer_state(self):
        return self.customer.state
    customer_state.short_description = 'state'

    def clean(self):
        original_order = Order.objects.filter(pk=self.pk).first()
        if original_order and (original_order.status == 'Delivered' or original_order.status == 'Cancelled'):
            raise ValidationError('Order status cannot be changed after cancellation or delivery.')
        


class ExtendOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    def customer_name(self):
        return self.order.customer.name

    customer_name.short_description = 'name'

  