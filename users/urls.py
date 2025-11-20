from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    register_view, login_view, user_profile_view,
    add_student_view, add_staff_view,
    list_students_view, list_staff_view,
    manage_student_view, manage_staff_view,
    HeadOfDepartmentListCreateView, HeadOfDepartmentDetailView,
    DepartmentHODView
)

app_name = 'users'

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('profile/', user_profile_view, name='profile'),
    path('add-student/', add_student_view, name='add_student'),
    path('add-staff/', add_staff_view, name='add_staff'),
    path('students/', list_students_view, name='list_students'),
    path('staff/', list_staff_view, name='list_staff'),
    path('students/<str:student_id>/', manage_student_view, name='manage_student'),
    path('staff/<str:staff_id>/', manage_staff_view, name='manage_staff'),
    
    # HOD Management URLs
    path('hods/', HeadOfDepartmentListCreateView.as_view(), name='hod_list_create'),
    path('hods/<int:id>/', HeadOfDepartmentDetailView.as_view(), name='hod_detail'),
    path('departments/<str:department>/hod/', DepartmentHODView.as_view(), name='department_hod'),
    
    # JWT Token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]