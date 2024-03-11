from django.urls import path
from .views import *
from . import views
app_name = 'myapp'
urlpatterns = [
    path('test',views.test, name='test'),
    path('login/', UserLoginView.as_view(), name = 'UserLoginView'),
    path('logout/', UserLogoutView.as_view(), name='UserLogoutView'),
    path('mycart/', MyCartView.as_view(), name='MyCartView'),
    path('testbarcode/', testbarcode.as_view(), name='testbarcode'),
    path('manage/<int:cp_id>/', ManageCartView.as_view(), name='ManageCartView'),
    path('checkout/', CheckoutView.as_view(), name='CheckoutView'),
    path('empty/', EmptyCartView.as_view(), name='EmptyCartView'),
    path('CategoryCreate',CategoryCreate.as_view(), name='CategoryCreate'),
    path('ProductCreate/', ProductCreate.as_view(), name='ProductCreate'),
]