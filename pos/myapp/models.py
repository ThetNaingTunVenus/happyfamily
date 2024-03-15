from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Test(models.Model):
    name = models.CharField(max_length=225)

    def __str__(self):
        return self.name

class Supplier(models.Model):
    supplier_name = models.CharField(max_length=225)
    phone_number = models.CharField(max_length=225)
    address = models.CharField(max_length=225)

    def __del__(self):
        return self.supplier_name

class Category(models.Model):
    category_name = models.CharField(max_length=225)

    def __str__(self):
        return self.category_name

class Items(models.Model):
    item_name = models.CharField(max_length=225)
    category = models.CharField(max_length=225)
    pruchase_price = models.IntegerField(default=0)
    sell_price = models.IntegerField(default=0)
    balance_qty = models.IntegerField(default=0)
    barcode_id = models.CharField(max_length=225,blank=True, null=True)
    photo = models.ImageField(upload_to='', blank=True, null=True)
    photo2 = models.ImageField(upload_to='', blank=True, null=True)
    photo3 = models.ImageField(upload_to='', blank=True, null=True)
    photo4 = models.ImageField(upload_to='', blank=True, null=True)
    itm_description = models.CharField(max_length=225,blank=True, null=True)

    def __str__(self):
        return self.item_name

class ItmColor(models.Model):
    items = models.ForeignKey(Items, on_delete=models.CASCADE)
    color = models.CharField(max_length=255,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.color

class ItmSize(models.Model):
    items = models.ForeignKey(Items, on_delete=models.CASCADE)
    size = models.CharField(max_length=255,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.size

class Cart(models.Model):
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.PositiveIntegerField(default=0)
    tax = models.PositiveIntegerField(default=0)
    super_total = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Items, on_delete=models.CASCADE)
    color = models.CharField(max_length=255,null=True, blank=True)
    size = models.CharField(max_length=255,null=True, blank=True)
    rate = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()
    remain_balance = models.IntegerField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return "Cart : "+ str(self.cart.id)+ "CartProduct : " + str(self.id)

STATUS=(
    ("Ordering","Ordering"),("Delivered","Delivered"),("Cash","Cash"),("Credit","Credit"),("Consignment","Consignment"),("Complete","Complete")
)

PAYMENT_TYPE = (
    ("Cash","Cash"),
("Credit","Credit"),
("Kpay","Kpay"),
("WavePay","WavePay"),
)

class DeliverySystem(models.Model):
    delivery_name = models.CharField(max_length=225)

    def __str__(self):
        return self.delivery_name

class Member(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    address = models.TextField(max_length=255)

    def __str__(self):
        return self.name

class Order(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    ordered_by = models.CharField(max_length=255,null=True, blank=True)
    shipping_address = models.CharField(max_length=255, null=True, blank=True)
    mobile = models.CharField(max_length=255,null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    subtotal = models.PositiveIntegerField()
    discount = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField()
    tax = models.PositiveIntegerField()
    delivery_fee = models.IntegerField(default=0)
    delivery_system = models.ForeignKey(DeliverySystem, on_delete=models.CASCADE, blank=True,null=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, blank=True,null=True)
    all_total = models.PositiveIntegerField()
    all_total_delivery = models.IntegerField(default=0)
    ordered_staus = models.CharField(max_length=255, choices=STATUS, default='Cash')
    payment = models.CharField(max_length=225, choices=PAYMENT_TYPE, default='Cash')
    deli_payment = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return "Order : " + str(self.id)


class PurchaseList(models.Model):
    supplier_name = models.CharField(max_length=225)
    item_name = models.CharField(max_length=225)
    purchase_qty = models.IntegerField(default=0)
    purchase_price = models.IntegerField(default=0)
    sale_price = models.IntegerField(default=0)
    logistic = models.IntegerField(default=0)
    total_purchase_price = models.IntegerField(default=0)
    p_date = models.DateField()
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.item_name