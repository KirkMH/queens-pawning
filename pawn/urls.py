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
    path('<int:pk>/delete',
         views.delete_pawn, name='delete_pawn'),
    path('<int:pk>/void',
         views.void_pawn, name='void_pawn'),

    path('<int:pk>/redeem', views.redeem_pawn, name='redeem_pawn'),
    path('<int:pk>/renew', views.renew_pawn, name='renew_pawn'),
    path('<int:pk>/payment', views.pawn_payment, name='pawn_payment'),
    path('<int:pk>/update_renew_redeem_date',
         views.update_renew_redeem_date, name='update_renew_redeem_date'),
    path('advance_interest', views.calculate_advance_interest,
         name='calculate_advance_interest'),

    path('inventory', views.inventory_list, name='inventory_list'),
    path('inventory/sdt_list', views.PawnedItemsDTListView.as_view(),
         name='pawneditems_dtlist'),
    path('inventory/print', views.print_inventory_list,
         name='print_inventory_list'),

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
