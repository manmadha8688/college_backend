from django.urls import path
from .views import (
    SubjectListCreateView, 
    SubjectDetailView,
    SyllabusListCreateView,
    SyllabusDetailView,
    DepartmentSubjectsView
)

urlpatterns = [
    # Subject endpoints
    path('subjects/', SubjectListCreateView.as_view(), name='subject-list-create'),
    path('subjects/<int:id>/', SubjectDetailView.as_view(), name='subject-detail'),
    
    # Syllabus endpoints
    path('syllabus/', SyllabusListCreateView.as_view(), name='syllabus-list-create'),
    path('syllabus/<int:id>/', SyllabusDetailView.as_view(), name='syllabus-detail'),
    
    # Department subjects endpoint
    path('department/<str:department>/', DepartmentSubjectsView.as_view(), name='department-subjects'),
]
