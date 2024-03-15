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

#sale
class SaleInvoiceCart(UserRequiredMixin, View):
    def post(self, request):
        pid = request.POST.get('pid')
        pqty = request.POST.get('quantity')
        product_obj = Items.objects.get(id=pid)
        product_id = product_obj.id
        subt = int(pqty) * int(product_obj.sell_price)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            this_product_in_cart = cart_obj.cartproduct_set.filter(product=product_obj)
            # Product already exists in cart
            if this_product_in_cart.exists():
                  
                cartproduct = this_product_in_cart.last()
                item_filter = Items.objects.filter(id=product_id)
                balance_filter = item_filter[0].balance_qty
                qty_balance = int(pqty)
                cart_sub_total = int(product_obj.sell_price) * int(pqty)
                cartproduct_balance = int(balance_filter) - int(qty_balance)
                item_update = Items.objects.filter(id=product_id)
                item_update.update(balance_qty=cartproduct_balance)
                # print('success !!!!!!')
                cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj,
                                                         rate=product_obj.sell_price, quantity=pqty,
                                                         subtotal=cart_sub_total,remain_balance=cartproduct_balance)

                # item_update = Items.objects.filter(id=product_id).update(balance_qty=cartproduct_balance)


                cart_obj.total += cart_sub_total
                cart_obj.tax = cart_obj.total * 0.00
                cart_obj.super_total = cart_obj.tax + cart_obj.total
                cart_obj.save()

                 

            # New item added in cart
            else:
                item_filter = Items.objects.filter(id=product_id)
                balance_filter = item_filter[0].balance_qty
                qty_balance = int(pqty)
                cart_sub_total = int(product_obj.sell_price) * int(pqty)
                cartproduct_balance = int(balance_filter) - int(qty_balance)
                item_update = Items.objects.filter(id=product_id)
                item_update.update(balance_qty=cartproduct_balance)
                # print('success !!!!!!')
                cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj,
                                                         rate=product_obj.sell_price, quantity=pqty,
                                                         subtotal=cart_sub_total,remain_balance=cartproduct_balance)

                # item_update = Items.objects.filter(id=product_id).update(balance_qty=cartproduct_balance)


                cart_obj.total += cart_sub_total
                cart_obj.tax = cart_obj.total * 0.00
                cart_obj.super_total = cart_obj.tax + cart_obj.total
                cart_obj.save()
        else:
            cart_obj = Cart.objects.create(total=0, staff=self.request.user)
            self.request.session['cart_id'] = cart_obj.id
            item_filter = Items.objects.filter(id=product_id)
            balance_filter = item_filter[0].balance_qty
            qty_balance = int(pqty)
            cart_sub_total = int(product_obj.sell_price) * int(pqty)
            cartproduct_balance = int(balance_filter) - int(qty_balance)
            cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.sell_price,
                                                     quantity=pqty, subtotal=cart_sub_total,remain_balance=cartproduct_balance)

            item_update = Items.objects.filter(id=product_id)
            item_update.update(balance_qty=cartproduct_balance)
            # cart_obj_total = 
            cart_obj.total += cart_sub_total
            cart_obj.tax = cart_obj.total * 0.00
            # print('succ')
            cart_obj.super_total = cart_obj.tax + cart_obj.total
            cart_obj.save()


        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        # context['cart'] = cart
        return redirect('myapp:MyCartView')

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


# ================= xhtml2pdf ===============
def pdf_invoice_create(request,id):
    ord_obj = Order.objects.get(id=id)
    template_path = 'pdf_invoice.html'
    context = {'ord_obj':ord_obj}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="invoice.pdf"'
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(
        html,dest=response,
    )
    if pisa_status.err:
        return HttpResponse('have a error pdf')
    return response
    
class InvoiceDetailView(UserRequiredMixin,DetailView):
    template_name = 'invoicedetail.html'
    model = Order
    context_object_name = 'ord_obj'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allstatus'] = STATUS

        return context


class InvoiceThermalPrintView(DetailView):
    template_name = 'test_slip.html'
    model = Order
    context_object_name = 'ord_obj'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allstatus'] = STATUS

        return context

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


######## Supplier ##############
class SupplierCreate(View):
    def get(self,request):
        supplier = Supplier.objects.all()
        context = {'supplier':supplier}
        return render(request,'supplier.html', context)
    def post(self,request):
        supplier_name = request.POST.get('supplier_name')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        message = None
        if not supplier_name:
            message = 'Please Enter Supplier Name'
        elif not phone_number:
            message = 'Please Enter Phone Number'
        elif not address:
            message = 'Enter Address'
        if not message:
            supplier_save = Supplier(supplier_name=supplier_name,phone_number=phone_number,address=address)
            supplier_save.save()
            success = 'Supplier Name create successfully'
            supplier = Supplier.objects.all()
            context = {'supplier': supplier,'success':success}
            return render(request, 'supplier.html', context)
        else:
            supplier = Supplier.objects.all()
            context = {'supplier': supplier, 'message': message}
            return render(request, 'supplier.html', context)

class SupplierEdit(UserRequiredMixin,View):
    def get(self,request, pk):
        pi = Supplier.objects.get(id=pk)
        fm = SupplierEditForm(instance=pi)
        return render(request,'supplieredit.html', {'form':fm})

    def post(self, request, pk):
        pi = Supplier.objects.get(id=pk)
        fm = SupplierEditForm(request.POST,instance=pi)
        if fm.is_valid():
            fm.save()
        return redirect('myapp:SupplierCreate')


class PurchaseCreateView(TemplateView):
    template_name = 'purchase_create_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #     # supplier id get from request url
        supplier_id = self.kwargs['id']
        # get car info
        supplier_data = Supplier.objects.get(id=supplier_id)

        context['supplier'] = Supplier.objects.get(id=supplier_id)
        context['item'] = Items.objects.all()
        context['supplier_list'] = PurchaseList.objects.filter(supplier_name=supplier_data.supplier_name)

        return context



class PurchaseData(View):
    def get(self,request):
        supplier = Supplier.objects.all()
        purchasedata = PurchaseList.objects.all()
        sum_purchase_qty = purchasedata.aggregate(Sum('purchase_qty'))['purchase_qty__sum']
        sum_purchase_price = purchasedata.aggregate(Sum('purchase_price'))['purchase_price__sum']
        sum_purchase_total = purchasedata.aggregate(Sum('total_purchase_price'))['total_purchase_price__sum']
        sum_logistic = purchasedata.aggregate(Sum('logistic'))['logistic__sum']
        context = {'supplier': supplier,
                   'purchasedata':purchasedata,
                   'sum_purchase_qty':sum_purchase_qty,
                   'sum_purchase_price':sum_purchase_price,
                   'sum_logistic':sum_logistic,
                   'sum_purchase_total':sum_purchase_total,
                   }
        return render(request, 'purchasedata.html',context)
    def post(self,request):
        suppliername = request.POST.get('suppliername')
        p_date = request.POST.get('p_date')
        item_name = request.POST.get('item_name')
        purchase_qty = request.POST.get('purchase_qty')
        purchase_price = request.POST.get('purchase_price')
        sale_price = request.POST.get('sale_price')
        logistic = request.POST.get('logistic')
        message = None
        if not p_date:
            message = 'please select Date'
        elif not item_name:
            message = 'please select Item'
        elif not purchase_qty:
            message = 'please enter quantity'
        elif not purchase_price:
            message = 'please enter purchase price'
        if not message:
            total_purchase_price =int(purchase_qty)*int(purchase_price)
            purchase_logistic = int(total_purchase_price)+int(logistic)
            purchase_list = PurchaseList(
                supplier_name=suppliername,
                item_name=item_name,
                purchase_qty=purchase_qty,
                purchase_price=purchase_price,
                sale_price=sale_price,
                logistic=logistic,
                p_date=p_date,
                total_purchase_price=purchase_logistic
            )
            purchase_list.save()
            item_balance = Items.objects.filter(item_name=item_name)
            balance_qty = item_balance[0].balance_qty
            total_balance = int(balance_qty)+int(purchase_qty)
            item_update = Items.objects.filter(item_name=item_name).update(pruchase_price=purchase_price,sell_price=sale_price,balance_qty=total_balance)
            return redirect(request.META['HTTP_REFERER'])
        else:
            context = {'message':message}
            # return redirect(request.META['HTTP_REFERER'])
            return render(request,'purchase_create_view.html',context)

class PurchaseReport(View):
    def post(self,request):
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        message = None
        if not fromdate:
            message='select from date'
        elif not todate:
            message = 'select to date'
        if not message:
            supplier = Supplier.objects.all()
            purchasedata = PurchaseList.objects.filter(p_date__range=[fromdate, todate])
            sum_purchase_qty = purchasedata.aggregate(Sum('purchase_qty'))['purchase_qty__sum']
            sum_purchase_price = purchasedata.aggregate(Sum('purchase_price'))['purchase_price__sum']
            sum_logistic = purchasedata.aggregate(Sum('logistic'))['logistic__sum']
            sum_purchase_total = purchasedata.aggregate(Sum('total_purchase_price'))['total_purchase_price__sum']
            context = {'supplier': supplier,
                       'purchasedata': purchasedata,
                       'sum_purchase_qty': sum_purchase_qty,
                       'sum_purchase_price': sum_purchase_price,
                       'sum_logistic':sum_logistic,
                       'sum_purchase_total':sum_purchase_total,
                       }
            return render(request, 'purchasedata.html', context)
        else:
            supplier = Supplier.objects.all()
            context = {'supplier': supplier, 'message':message}
            return render(request, 'purchasedata.html', context)



class PurchaseDataDelete(View):
    def get(self,request,pk):
        pi = PurchaseList.objects.get(id=pk)
        fm = PurchaseDataDeleteFrom(instance=pi)
        return render(request, 'purchase_data_delete.html', {'form': fm})

    def post(self, request,pk):
        pi = PurchaseList.objects.get(id=pk)
        item = Items.objects.get(item_name=pi.item_name)
        item_n = item.balance_qty
        pur_qty = pi.purchase_qty
        remain_item_qty = int(item_n)-int(pur_qty)
        item_update = Items.objects.filter(item_name=pi.item_name).update(balance_qty=remain_item_qty)
        pi.delete()
        return redirect('myapp:PurchaseData')

class CreateMember(View):
    def get(self, request):
        fm = MemberForm()
        m = Member.objects.all()
        return render(request, 'CreateMember.html', {'m':m, 'form':fm})

    def post(self, request):
        fm = MemberForm(request.POST)
        if fm.is_valid():
            fm.save()
        return redirect(request.META['HTTP_REFERER'])

class CreditMemberReport(View):
    def get(self, request):
        mem = Member.objects.all()
        ord = Order.objects.filter(payment="Credit")
        context = {'mem':mem, 'ord':ord}
        return render(request, 'CreditMemberReport.html', context)
    
    def post(self, request):
        mn = request.POST.get('mn')
        if mn == "":
            return redirect(request.META['HTTP_REFERER'])
        else:
            mem = Member.objects.all()
            mem_obj = Member.objects.get(id=mn)
            ord = Order.objects.filter(payment="Credit", member=mem_obj)
            context = {'ord':ord,'mem':mem}
            return render(request, 'CreditMemberReport.html', context)

class CreditBillPayment(View):
    def post(self, request):
        i = request.POST.get('invid')
        ord_id = Order.objects.get(id=i)
        ord_id.payment = "Cash"
        ord_id.save()
        return redirect(request.META['HTTP_REFERER'])
