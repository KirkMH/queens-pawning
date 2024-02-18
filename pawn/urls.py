from django.urls import path
from . import views


urlpatterns = [
    path('', views.pawn_list, name='pawn_list'),
    path('dt_list', views.PawnDTListView.as_view(), name='pawn_dtlist'),
    path('new', views.PawnCreateView.as_view(), name='new_pawn'),
    path('<int:pk>/edit',
         views.PawnUpdateView.as_view(), name='edit_pawn'),
    path('<int:pk>/detail',
         views.PawnDetailView.as_view(), name='pawn_detail'),
    path('<int:pk>/payment', views.pawn_payment, name='pawn_payment'),

    path('inventory', views.inventory_list, name='inventory_list'),
    path('inventory/sdt_list', views.PawnedItemsDTListView.as_view(),
         name='pawneditems_dtlist'),

    path('discounts/<int:pk>/request',
         views.request_discount, name='request_discount'),            # pk -> pawn.pk
    path('discounts/<int:pk>/status', views.request_discount_status,
         name='request_discount_status'),                             # pk -> pawn.pk
    path('discounts/<int:pk>/cancel', views.cancel_request_discount,
         name='cancel_request_discount'),                             # pk -> pawn.pk
    path('discounts/<int:pk>/approve',
         views.approve_discount, name='approve_discount'),            # pk -> discount.pk
    path('discounts/<int:pk>/reject', views.reject_discount,
         name='reject_discount'),                                     # pk -> discount.pk
    path('discounts', views.discount_requests, name='discount_list'),
    path('discounts/dt_list', views.DiscountRequestsDTListView.as_view(),
         name='discount_dtlist'),

]
