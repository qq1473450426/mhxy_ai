from django.urls import path
from . import views

urlpatterns=[
    path('',views.dashboard,name='dashboard'),
    path('accounts/add/',views.add_account,name='add_account'),
    path('accounts/<int:pk>/start/',views.start,name='start'),
    path('accounts/<int:pk>/stop/',views.stop,name='stop'),
    path('accounts/<int:pk>/logs/',views.logs,name='logs'),
    path('accounts/<int:pk>/task/',views.task,name='task'),
    path('api/status/',views.status,name='status'),
    path('api/windows/',views.windows,name='windows'),
]
