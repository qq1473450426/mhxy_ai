from django.urls import path
from . import views
from . import account_api
from . import live_api
from . import screenshot_api
from . import stream_api
from . import runtime_api
from engine import desktop_api

urlpatterns = [
    path('api/overview/', views.overview),
    path('api/tasks/', views.tasks), path('api/tasks/<int:pk>/', views.task_detail), path('api/tasks/<int:pk>/action/', views.task_action),
    path('api/knowledge/search/', views.knowledge_search), path('api/leveling/strategy/', views.leveling_strategy), path('api/leveling/observe/', views.leveling_observe),
    path('api/accounts/', account_api.accounts), path('api/accounts/<int:pk>/', account_api.account_detail), path('api/accounts/<int:pk>/action/', account_api.account_action),
    path('api/accounts/control/', account_api.control), path('api/multibox/health/', account_api.multibox_health), path('api/windows/', views.windows),
    path('api/live/', live_api.live_snapshot), path('api/live/stream/', stream_api.live_stream),
    path('api/accounts/<int:pk>/screenshot/', screenshot_api.account_screenshot),
    path('api/runtimes/', runtime_api.runtimes), path('api/runtimes/control/', runtime_api.runtime_control),
    path('api/desktop/windows/', desktop_api.windows), path('api/desktop/select/', desktop_api.select_window),
    path('api/desktop/<int:account_id>/snapshot/', desktop_api.desktop_snapshot), path('api/desktop/<int:account_id>/step/', desktop_api.desktop_step),
]
