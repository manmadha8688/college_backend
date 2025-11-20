from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission
from .models import Subject, Syllabus, DEPARTMENT_CHOICES
from .serializers import SubjectSerializer, SyllabusSerializer
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework.views import APIView

class IsStaffOrReadOnly(BasePermission):
    """
    Permission class that allows read-only access to any authenticated user,
    but only allows write access to staff members.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff

class SubjectListCreateView(generics.ListCreateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(
                    serializer.data, 
                    status=status.HTTP_201_CREATED, 
                    headers=headers
                )
            except Exception as e:
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            
class SubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    lookup_field = 'id'

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        pdf_url = request.data.get('pdf_url')
        
        # Handle syllabus update or creation
        if pdf_url:
            syllabus, created = Syllabus.objects.get_or_create(
                subject=instance,
                defaults={'pdf_url': pdf_url}
            )
            if not created:
                syllabus.pdf_url = pdf_url
                syllabus.save()
        
        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SyllabusListCreateView(generics.ListCreateAPIView):
    queryset = Syllabus.objects.select_related('subject').all()
    serializer_class = SyllabusSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by department if provided
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(subject__department=department)
            
        # Filter by semester if provided
        semester = self.request.query_params.get('semester')
        if semester:
            queryset = queryset.filter(subject__semester=semester)
            
        return queryset
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        subject_id = request.data.get('subject')
        pdf_url = request.data.get('pdf_url')
        
        if not subject_id or not pdf_url:
            return Response(
                {'error': 'Both subject ID and PDF URL are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            return Response(
                {'error': 'Subject not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Check if syllabus already exists for this subject
        syllabus, created = Syllabus.objects.update_or_create(
            subject=subject,
            defaults={'pdf_url': pdf_url}
        )
        
        serializer = self.get_serializer(syllabus)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class SyllabusDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Syllabus.objects.select_related('subject').all()
    serializer_class = SyllabusSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    lookup_field = 'id'


class DepartmentSubjectsView(generics.ListAPIView):
    """
    View to list all subjects for a specific department.
    Optionally filter by semester if provided in query params.
    """
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        department = self.kwargs.get('department')
        
        # Normalize department code to uppercase
        if department:
            department = department.upper()
            
        # Use the imported DEPARTMENT_CHOICES
        valid_departments = dict(DEPARTMENT_CHOICES).keys()
        
        if department not in valid_departments:
            raise serializers.ValidationError({
                'department': f'Invalid department code. Must be one of: {list(valid_departments)}',
                'valid_departments': list(valid_departments)  # Include valid options in response
            })
        
        queryset = Subject.objects.filter(department=department).prefetch_related('syllabus')
        
        # Get semester from query params if provided
        semester = self.request.query_params.get('semester')
        if semester:
            try:
                semester = int(semester)
                queryset = queryset.filter(semester=semester)
            except (ValueError, TypeError):
                raise serializers.ValidationError({
                    'semester': 'Semester must be a number between 1 and 8',
                    'valid_semesters': list(range(1, 9))  # Include valid options in response
                })
            
        return queryset
