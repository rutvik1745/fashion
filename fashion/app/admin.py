from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Customer,
    Category,
    SubCategory,
    Product,
    Cart,
    Order,
    ExtendOrder
    
)

@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display =['user_id','id','user','name','state','city','zipcode','mobile','address']
    search_fields=['name','state','city']
    list_per_page=10

@admin.register(Category)
class CategoryModelAdmin(admin.ModelAdmin):
    list_display=['id','cat_name']
    list_per_page=10

@admin.register(SubCategory)
class SubCategoryModelAdmin(admin.ModelAdmin):
    list_display=['id','sub_cat_name']
    list_per_page=10

@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display=['id','subcategory','name','category'
    ,'description','brand','image1','image2','image3','image4']
    list_editable=['description']
    search_fields=['name','brand','description']
    list_per_page=10
    list_filter=['category','subcategory']



@admin.register(Cart)
class ModelAdmin(admin.ModelAdmin):
    
    readonly_fields = ['id', 'user', 'product', 'quantity']
    list_display = ['id','user','product','quantity']
    list_per_page=10
    actions = None # Disable all actions

    
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

   

class ExtendOrderInline(admin.TabularInline):
    model = ExtendOrder
    extra = 0
    show_change_link = True
    readonly_fields = ('customer', 'user')

    def customer(self, instance):
        return instance.order.customer

    def user(self, instance):
        return instance.order.user

@admin.register(Order)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','customer_name','customer_address','customer_city','customer_state','customer_zipcode','order_date','status']
    list_editable=['status']
    list_filter=['status',]
    list_per_page=10

@admin.register(ExtendOrder)
class ExtendOderModelAdmin(admin.ModelAdmin):
    list_display = ['order', 'id','user','customer_name','product', 'quantity']
    list_select_related = ('order', 'order__customer', 'order__user')
    # readonly_fields = ('customer', 'user')
    list_per_page=10

    def customer(self, instance):
        return instance.order.customer

    def user(self, instance):
        return instance.order.user

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('order__customer', 'order__user')

