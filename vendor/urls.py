from django.urls import path
from .views import CreateUserView, VendorView, VendorByIdView

urlpatterns = [
    path('user/register/', CreateUserView.as_view(), name='register'),
    path('vendors/', VendorView.as_view(), name='vendors'),
    path('vendors/<int:vendor_id>/', VendorByIdView.as_view(), name='vendor_by_id')
]