from django.urls import path
from . import views

urlpatterns = [
    path('', views.CategoryListView.as_view(), name='category-list'),
    path('<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('create/', views.CategoryCreateView.as_view(), name='category-create'),
    path('<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category-edit'),
    path('<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category-delete'),
]