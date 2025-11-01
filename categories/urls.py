from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    # /categories/
    path('', views.CategoryListView.as_view(), name='category-list'),
    
    # /categories/create/
    path('create/', views.CategoryCreateView.as_view(), name='category-create'),
    
    # /categories/5/ (Example detail view)
    path('<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # /categories/5/edit/
    path('<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category-edit'),
    
    # /categories/5/delete/
    path('<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category-delete'),
]