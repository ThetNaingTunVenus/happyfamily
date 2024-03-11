import datetime

from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.db.models import Sum,Count,F
from django.http import HttpResponse
from django.views.generic import TemplateView, View, CreateView, DetailView,FormView
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.paginator import Paginator

from .forms import *
from .models import *

#html2pdf
from django.template.loader import get_template
from xhtml2pdf import pisa

# Create your views here.
def test(request):
    return render(request, 'base.html')


#test for barcode
class testbarcode(View):
    def post(self,request):
        product_idb = request.POST.get('pid')
        message = None
        if not product_idb:
            message = 'barcode is blank'
        if not message:
            product_obj = Items.objects.get(barcode_id=product_idb)
            product_id = product_obj.id
            # print(product_id)
            cart_id = self.request.session.get("cart_id", None)
            if cart_id:
                cart_obj = Cart.objects.get(id=cart_id)
                this_product_in_cart = cart_obj.cartproduct_set.filter(product=product_obj)
                # Product already exists in cart
                if this_product_in_cart.exists():
                    cartproduct = this_product_in_cart.last()
                    cartproduct.quantity += 1
                    cartproduct.subtotal += product_obj.sell_price
                    cartproduct.remain_balance -= 1

                    cartproduct.save()
                    cart_obj.total += product_obj.sell_price
                    cart_obj.tax = cart_obj.total * 0.00
                    cart_obj.super_total = cart_obj.tax + cart_obj.total
                    cart_obj.save()
                    cartproduct_balance = cartproduct.remain_balance
                    # print('update')
                    item_update = Items.objects.filter(id=product_id).update(balance_qty=cartproduct_balance)
                # New item added in cart
                else:
                    item_filter = Items.objects.filter(id=product_id)
                    balance_filter = item_filter[0].balance_qty
                    qty_balance = 1
                    cartproduct_balance = int(balance_filter) - int(qty_balance)
                    item_update = Items.objects.filter(id=product_id)
                    item_update.update(balance_qty=cartproduct_balance)
                    # print('success !!!!!!')
                    cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj,
                                                             rate=product_obj.sell_price, quantity=1,
                                                             subtotal=product_obj.sell_price,
                                                             remain_balance=cartproduct_balance)

                    # item_update = Items.objects.filter(id=product_id).update(balance_qty=cartproduct_balance)

                    cart_obj.total += product_obj.sell_price
                    cart_obj.tax = cart_obj.total * 0.00
                    cart_obj.super_total = cart_obj.tax + cart_obj.total
                    cart_obj.save()
            else:
                cart_obj = Cart.objects.create(total=0, staff=request.user)
                self.request.session['cart_id'] = cart_obj.id
                item_filter = Items.objects.filter(id=product_id)
                balance_filter = item_filter[0].balance_qty
                qty_balance = 1
                cartproduct_balance = int(balance_filter) - int(qty_balance)
                cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj,
                                                         rate=product_obj.sell_price,
                                                         quantity=1, subtotal=product_obj.sell_price,
                                                         remain_balance=cartproduct_balance)

                item_update = Items.objects.filter(id=product_id)
                item_update.update(balance_qty=cartproduct_balance)

                cart_obj.total += product_obj.sell_price
                cart_obj.tax = cart_obj.total * 0.00
                # print('succ')
                cart_obj.super_total = cart_obj.tax + cart_obj.total
                cart_obj.save()
            cart_id = self.request.session.get('cart_id', None)
            if cart_id:
                cart = Cart.objects.get(id=cart_id)
            else:
                cart = None
            context = {'cart': cart, 'message': message}

            return render(request, 'mycartview.html', context)
        else:
            return render(request, 'mycartview.html', {'message':message})




class UserRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            pass
        else:
            return redirect('myapp:UserLoginView')
        return super().dispatch(request, *args, **kwargs)


class UserLoginView(FormView):
    template_name = 'login.html'
    form_class = ULoginForm
    success_url = reverse_lazy('myapp:MyCartView')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data['password']
        usr = authenticate(username=username, password=password)

        if usr is not None:
            login(self.request, usr)

        else:
            return render(self.request, self.template_name, {'form': self.form_class, 'error': 'Invalid user login!'})
        return super().form_valid(form)

class UserLogoutView(View):
    def get(self,request):
        logout(request)
        return redirect('myapp:UserLoginView')

class MyCartView(UserRequiredMixin,TemplateView):
    template_name = 'mycartview.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart
        context['product_list'] = Items.objects.all().order_by('-id')
        context['queryset'] = Order.objects.filter(created_at=datetime.date.today()).order_by('-id')
        # context['ord'] = EcommerceOrder.objects.filter(orderstatus=1).order_by('-id')
        # context['allord'] = EcommerceOrder.objects.all().order_by('-id')
        return context



class ManageCartView(UserRequiredMixin,View):
    def get(self, request, *args, **kwargs):

        cp_id = kwargs['cp_id']
        action = request.GET.get('action')
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart

        if action == "inc":
            cp_obj.quantity +=1
            cp_obj.remain_balance -=1
            item_balance = cp_obj.remain_balance
            item_update = Items.objects.filter(id=cp_obj.product.id).update(balance_qty=item_balance)
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total +=cp_obj.rate
            cart_obj.tax = cart_obj.total * 0.00
            cart_obj.super_total = cart_obj.tax + cart_obj.total
            cart_obj.save()
        elif action == 'dcr':
            cp_obj.quantity -= 1
            cp_obj.remain_balance += 1
            item_balance = cp_obj.remain_balance
            item_update = Items.objects.filter(id=cp_obj.product.id).update(balance_qty=item_balance)
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.tax = cart_obj.total * 0.00
            cart_obj.super_total = cart_obj.tax + cart_obj.total
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()
        elif action == 'rmv':
            cart_obj.total -= cp_obj.subtotal
            # cp_obj.remain_balance += cp_obj.quantity
            item_balance = cp_obj.remain_balance +cp_obj.quantity

            item_update = Items.objects.filter(id=cp_obj.product.id).update(balance_qty=item_balance)
            cart_obj.tax = cart_obj.total * 0.00
            cart_obj.super_total = cart_obj.tax + cart_obj.total
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect('myapp:MyCartView')


class EmptyCartView(UserRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)

            cart.cartproduct_set.all().delete()
            cart.total =0
            cart.tax = 0
            cart.super_total=0
            cart.save()
        return redirect('myapp:MyCartView')



class CheckoutView(UserRequiredMixin,CreateView):
    template_name = 'checkout.html'
    form_class = CheckoutForm
    success_url = reverse_lazy('myapp:MyCartView')

    # def dispatch(self, request, *args, **kwargs):
    #     if request.user.is_authenticated and request.user.customer:
    #         print('login....')
    #     else:
    #         return redirect('/login/?next=/checkout/')
    #     return super().dispatch(request, *args, **kwargs)

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
        cart_id = self.request.session.get('cart_id')
        # print(form.instance.delivery_fee)
        deli = form.instance.delivery_fee
        dis = form.instance.discount
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            # form.instance.discount = 0
            form.instance.total = cart_obj.total

            # form.instance.ordered_staus = 'Cash'
            form.instance.tax = cart_obj.tax
            form.instance.all_total = cart_obj.super_total
            total_deli = deli + cart_obj.super_total - dis
            form.instance.all_total_delivery = total_deli

            del self.request.session['cart_id']
        else:
            return redirect('myapp:MyCartView')
        return super().form_valid(form)

class CategoryCreate(View):
    def get(self,request):
        category = Category.objects.all()
        item_list = Items.objects.all()
        message = None
        context = {'item_list': item_list, 'category': category, 'message': message}
        return render(request, 'categorycreate.html', context)
    def post(self,request):
        category_name = request.POST.get('category_name')
        message = None
        if not category_name:
            message = 'please enter category name'
        if not message:
            cate = Category(category_name=category_name)
            cate.save()
            return redirect(request.META['HTTP_REFERER'])
        else:
            category = Category.objects.all()
            message = 'please enter category name'
            return render(request, 'categorycreate.html', {'message':message,'category':category})

class ProductCreate(View):
    def get(self,request):
        category = Category.objects.all()
        item_list = Items.objects.all()
        message = None
        context = {'item_list':item_list,'category':category,'message':message}
        return render(request, 'productcreate.html', context)
    def post(self,request):
        item_name = request.POST.get('item_name')
        category = request.POST.get('category')
        purchase_price = request.POST.get('purchase_price')
        sale_price = request.POST.get('sale_price')
        barcode_id = request.POST.get('barcode_id')
        itm_description = request.POST.get('itmdesc')

        message = None
        if not item_name:
            message = 'please enter item'
        if not message:
            item = Items(item_name=item_name,category=category,pruchase_price=purchase_price,sell_price=sale_price,barcode_id=barcode_id,itm_description=itm_description)
            item.save()
            return redirect(request.META['HTTP_REFERER'])
        else:
            category = Category.objects.all()
            item_list = Items.objects.all()
            context = {'message': message,'category':category,'item_list':item_list}
            return render(request, 'productcreate.html', context)