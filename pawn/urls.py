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
]
