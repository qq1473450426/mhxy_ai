from django.urls import path
from . import views
urlpatterns=[path('',views.dashboard),path('accounts/add/',views.add_account),path('accounts/<int:pk>/start/',views.start),path('accounts/<int:pk>/stop/',views.stop),path('accounts/<int:pk>/logs/',views.logs),path('api/status/',views.status),path('api/windows/',views.windows)]
