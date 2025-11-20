from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.utils import timezone
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging
from .serializers import (
    UserRegistrationSerializer, UserSerializer, LoginSerializer,
    StudentRegistrationSerializer, StaffRegistrationSerializer,
    StudentSerializer, StaffSerializer, HeadOfDepartmentSerializer
)
from .models import User, Student, Staff, HeadOfDepartment

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Register a new user
    POST /api/auth/register/
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        # Check if trying to create admin user
        role = serializer.validated_data.get('role')
        if role == 'admin':
            # Only existing admins can create admin users
            # For now, we'll allow it but you can add permission check here
            # if not request.user.is_authenticated or request.user.role != 'admin':
            #     return Response(
            #         {"error": "Only admins can create admin users."},
            #         status=status.HTTP_403_FORBIDDEN
            #     )
            pass
        
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login user and return JWT tokens
    POST /api/auth/login/
    """
    logger.info("Login attempt")
    
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        logger.warning(f"Serializer validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    
    logger.info("Processing login attempt")
    
    # Try to get user by email first
    try:
        user = User.objects.get(email=email)
        logger.info("User found during login")
    except User.DoesNotExist:
        logger.warning("User not found during login")
        return Response(
            {'error': 'Invalid email or password.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Check if user is active
    if not user.is_active:
        logger.warning("Inactive user login attempt")
        return Response(
            {'error': 'User account is disabled.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check password directly
    if not user.check_password(password):
        logger.warning("Invalid login attempt")
        return Response(
            {'error': 'Invalid email or password.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Password is correct, generate JWT tokens
    logger.info("Login successful")
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'message': 'Login successful',
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    """
    Get current user profile
    GET /api/auth/profile/
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_student_view(request):
    """
    Add a new student (Admin and Staff only)
    POST /api/auth/add-student/
    """
    # Check if user has permission (admin or staff)
    if request.user.role not in ['admin', 'staff']:
        return Response(
            {'error': 'You do not have permission to add students.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    logger.info("Processing add student request")
    serializer = StudentRegistrationSerializer(data=request.data)
    
    if not serializer.is_valid():
        logger.warning(f"Serializer validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        student = serializer.save()
        logger.info("Student created successfully")
        return Response({
            'message': 'Student created successfully',
            'student': StudentSerializer(student).data
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error("Error creating student", exc_info=True)
        return Response(
            {'error': f'Failed to create student: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_staff_view(request):
    """
    Add a new staff member (Admin only)
    POST /api/auth/add-staff/
    """
    # Check if user has permission (admin only)
    if request.user.role != 'admin':
        return Response(
            {'error': 'Only admins can add staff members.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    logger.info("Processing add staff request")
    serializer = StaffRegistrationSerializer(data=request.data)
    
    if not serializer.is_valid():
        logger.warning(f"Serializer validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        staff = serializer.save()
        logger.info("Staff created successfully")
        return Response({
            'message': 'Staff member created successfully',
            'staff': StaffSerializer(staff).data
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error("Error creating staff", exc_info=True)
        return Response(
            {'error': f'Failed to create staff: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_students_view(request):
    """
    List all students (Admin only)
    GET /api/auth/students/
    """
    # Check if user has permission (admin only)
    if request.user.role != 'admin':
        return Response(
            {'error': 'Only admins can view all students.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    students = Student.objects.all().order_by('-user__date_joined')
    serializer = StudentSerializer(students, many=True)
    return Response({
        'count': students.count(),
        'students': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_staff_view(request):
    """
    List all staff members (Admin only)
    GET /api/auth/staff/
    """
    # Check if user has permission (admin only)
    if request.user.role != 'admin':
        return Response(
            {'error': 'Only admins can view all staff members.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    staff_members = Staff.objects.all().order_by('-user__date_joined')
    serializer = StaffSerializer(staff_members, many=True)
    return Response({
        'count': staff_members.count(),
        'staff': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_student_view(request, student_id):
    """
    Update or delete a student (Admin only)
    PUT/PATCH /api/auth/students/<student_id>/
    DELETE /api/auth/students/<student_id>/
    """
    # Check if user has permission (admin only)
    if request.user.role != 'admin':
        return Response(
            {'error': 'Only admins can manage students.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        student = Student.objects.get(student_id=student_id)
    except Student.DoesNotExist:
        return Response(
            {'error': 'Student not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method in ['PUT', 'PATCH']:
        # For partial updates, use partial=True
        partial = request.method == 'PATCH'
        serializer = StudentSerializer(
            student, 
            data=request.data, 
            partial=partial,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            updated_student = serializer.save()
            return Response({
                'message': 'Student updated successfully',
                'student': StudentSerializer(updated_student).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Failed to update student: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    elif request.method == 'DELETE':
        try:
            # Delete the associated user
            user = student.user
            student.delete()
            user.delete()
            return Response(
                {'message': 'Student deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to delete student: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

@api_view(['PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_staff_view(request, staff_id):
    """
    Update or delete a staff member (Admin only)
    PUT/PATCH /api/auth/staff/<staff_id>/
    DELETE /api/auth/staff/<staff_id>/
    """
    # Check if user has permission (admin only)
    if request.user.role != 'admin':
        return Response(
            {'error': 'Only admins can manage staff members.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        staff = Staff.objects.get(staff_id=staff_id)
    except Staff.DoesNotExist:
        return Response(
            {'error': 'Staff member not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method in ['PUT', 'PATCH']:
        # For partial updates, use partial=True
        partial = request.method == 'PATCH'
        serializer = StaffSerializer(
            staff, 
            data=request.data, 
            partial=partial,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            updated_staff = serializer.save()
            return Response({
                'message': 'Staff member updated successfully',
                'staff': StaffSerializer(updated_staff).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Failed to update staff member: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    elif request.method == 'DELETE':
        try:
            # Delete the associated user
            user = staff.user
            staff.delete()
            user.delete()
            return Response(
                {'message': 'Staff member deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to delete staff member: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class HeadOfDepartmentListCreateView(generics.ListCreateAPIView):
    """
    List all HODs or create a new HOD appointment (Admin only)
    GET /api/auth/hods/
    POST /api/auth/hods/
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = HeadOfDepartmentSerializer
    # Initialize HOD view
    
    # In users/views.py, update the get_queryset method:

    def get_queryset(self):
        """Return all HODs with related staff and user data"""
        queryset = HeadOfDepartment.objects.select_related(
            'staff', 
            'staff__user'
        ).all()
    
    # Existing filtering code...
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department=department)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('department', '-is_active', '-start_date')   
    def perform_create(self, serializer):
        """Create a new HOD appointment"""
        # Set start date to current date if not provided
        if 'start_date' not in serializer.validated_data:
            serializer.validated_data['start_date'] = timezone.now().date()
        serializer.save()


class HeadOfDepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a HOD appointment (Admin only)
    GET /api/auth/hods/<id>/
    PUT /api/auth/hods/<id>/
    PATCH /api/auth/hods/<id>/
    DELETE /api/auth/hods/<id>/
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = HeadOfDepartmentSerializer
    queryset = HeadOfDepartment.objects.all()
    lookup_field = 'id'
    
    def perform_update(self, serializer):
        """Update a HOD appointment"""
        # If making the HOD inactive, set end date to current date
        if 'is_active' in serializer.validated_data and not serializer.validated_data['is_active']:
            serializer.validated_data['end_date'] = timezone.now().date()
        serializer.save()
    
    def perform_destroy(self, instance):
        """Delete a HOD appointment"""
        # Instead of deleting, set as inactive and set end date
        instance.is_active = False
        instance.end_date = timezone.now().date()
        instance.save()


class DepartmentHODView(APIView):
    """
    Get the current HOD for a department
    GET /api/auth/departments/<department>/hod/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, department):
        """Get the current HOD for the specified department"""
        try:
            hod = HeadOfDepartment.objects.get(
                department=department,
                is_active=True
            )
            serializer = HeadOfDepartmentSerializer(hod)
            return Response(serializer.data)
        except HeadOfDepartment.DoesNotExist:
            return Response(
                {'detail': f'No active HOD found for {department} department'},
                status=status.HTTP_404_NOT_FOUND
            )

