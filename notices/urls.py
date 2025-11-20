from django.urls import path
from .views import (
    create_notice_view, list_notices_view, 
    notice_detail_view, manage_notice_view
)

app_name = 'notices'

urlpatterns = [
    path('create/', create_notice_view, name='create'),
    path('', list_notices_view, name='list'),
    path('<int:notice_id>/', notice_detail_view, name='detail'),
    path('manage/<int:notice_id>/', manage_notice_view, name='manage'),
]

