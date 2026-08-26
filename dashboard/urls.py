from django.urls import path
from . import views
from . import account_api

urlpatterns = [
    path('api/overview/', views.overview),
    path('api/tasks/', views.tasks), path('api/tasks/<int:pk>/', views.task_detail),
    path('api/tasks/<int:pk>/action/', views.task_action),
    path('api/knowledge/search/', views.knowledge_search),
    path('api/leveling/strategy/', views.leveling_strategy),
    path('api/leveling/observe/', views.leveling_observe),
    path('api/accounts/', account_api.accounts),
    path('api/accounts/<int:pk>/', account_api.account_detail),
    path('api/accounts/<int:pk>/action/', account_api.account_action),
    path('api/multibox/health/', account_api.multibox_health),
    path('api/windows/', views.windows),
]
