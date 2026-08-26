from django.urls import path
from . import views

urlpatterns = [
    path('api/overview/', views.overview),
    path('api/tasks/', views.tasks), path('api/tasks/<int:pk>/', views.task_detail),
    path('api/tasks/<int:pk>/action/', views.task_action),
    path('api/knowledge/search/', views.knowledge_search),
    path('api/leveling/strategy/', views.leveling_strategy),
    path('api/accounts/', views.accounts), path('api/accounts/<int:pk>/action/', views.account_action),
    path('api/windows/', views.windows),
]
