from django.urls import path
from . import views


urlpatterns = [
    path('', views.pawn_list, name='pawn_list'),
    path('dt_list/', views.PawnDTListView.as_view(), name='pawn_dtlist'),
    path('new/', views.PawnCreateView.as_view(), name='new_pawn'),
    path('<int:pk>/edit',
         views.PawnUpdateView.as_view(), name='edit_pawn'),

]
