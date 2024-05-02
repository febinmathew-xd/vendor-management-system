from django.urls import path
from .views import CreateUserView, VendorView, VendorByIdView, PurchaseOrderView, PurchaseOrderByIdView

urlpatterns = [
    path('user/register/', CreateUserView.as_view(), name='register'),
    path('vendors/', VendorView.as_view(), name='vendors'),
    path('vendors/<int:vendor_id>/', VendorByIdView.as_view(), name='vendor_by_id'),
    path('purchase_orders/', PurchaseOrderView.as_view(), name='purchase_order'),
    path('purchase_orders/<int:po_id>/', PurchaseOrderByIdView.as_view(), name='purchase_order_by_id')
]