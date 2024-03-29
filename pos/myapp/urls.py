from django.urls import path
from .views import *
from . import views
app_name = 'myapp'
urlpatterns = [
    path('',views.test, name='test'),
    path('login/', UserLoginView.as_view(), name = 'UserLoginView'),
    path('logout/', UserLogoutView.as_view(), name='UserLogoutView'),
    #sale
    path('mycart/', MyCartView.as_view(), name='MyCartView'),
    path('testbarcode/', testbarcode.as_view(), name='testbarcode'),
    path('SaleInvoiceCart/', SaleInvoiceCart.as_view(), name='SaleInvoiceCart'),
    path('manage/<int:cp_id>/', ManageCartView.as_view(), name='ManageCartView'),
    path('checkout/', CheckoutView.as_view(), name='CheckoutView'),
    path('empty/', EmptyCartView.as_view(), name='EmptyCartView'),
    path('CategoryCreate',CategoryCreate.as_view(), name='CategoryCreate'),
    path('ProductCreate/', ProductCreate.as_view(), name='ProductCreate'),

    #member
    path('CreateMember/', CreateMember.as_view(), name='CreateMember'),
    path('CreditMemberReport/', CreditMemberReport.as_view(), name='CreditMemberReport'),
    path('CreditBillPayment/', CreditBillPayment.as_view(), name='CreditBillPayment'),

    #purchase
    path('SupplierCreate/', SupplierCreate.as_view(), name='SupplierCreate'),
    path('SupplierEdit/<int:pk>/', SupplierEdit.as_view(), name='SupplierEdit'),
    path('PurchaseCreateView/<int:id>/', PurchaseCreateView.as_view(), name='PurchaseCreateView'),
    path('PurchaseData/', PurchaseData.as_view(), name='PurchaseData'),
    path('PurchaseReport/', PurchaseReport.as_view(), name='PurchaseReport'),
    path('PurchaseDataDelete/<int:pk>/', PurchaseDataDelete.as_view(), name='PurchaseDataDelete'),
    path('pdf_invoice_create/<int:id>/', pdf_invoice_create, name='pdf_invoice_create'),
    path('InvoiceDetailView/<int:pk>/', InvoiceDetailView.as_view(), name='InvoiceDetailView'),
    path('InvoiceThermalPrintView/<int:pk>/', InvoiceThermalPrintView.as_view(), name='InvoiceThermalPrintView'),

    #Report


]