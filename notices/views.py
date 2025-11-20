from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import logging
from .models import Notice
from .serializers import NoticeSerializer, NoticeCreateSerializer

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_notice_view(request):
    """
    Create a new notice (Admin and Staff only)
    POST /api/notices/create/
    """
    # Check if user has permission (admin or staff)
    if request.user.role not in ['admin', 'staff']:
        return Response(
            {'error': 'Only staff and admin can create notices.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Log minimal information for security
    serializer = NoticeCreateSerializer(data=request.data, context={'request': request})
    
    if not serializer.is_valid():
        logger.warning("Serializer validation failed")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        notice = serializer.save()
        logger.info("Notice created successfully")
        return Response({
            'message': 'Notice created successfully',
            'notice': NoticeSerializer(notice).data
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error("Error creating notice", exc_info=True)
        return Response(
            {'error': f'Failed to create notice: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_notices_view(request):
    """
    List notices based on user role
    GET /api/notices/
    """
    user = request.user
    # Filter notices based on user role
    if user.role == 'admin' or user.role == 'staff':
        # Staff and admin can see all notices
        notices = Notice.objects.all().order_by('-created_at')
    else:
        # Students can only see "all users" notices
        notices = Notice.objects.filter(audience='all').order_by('-created_at')
    serializer = NoticeSerializer(notices, many=True)
    return Response({
        'count': notices.count(),
        'notices': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notice_detail_view(request, notice_id):
    """
    Get a specific notice
    GET /api/notices/{id}/
    """
    try:
        notice = Notice.objects.get(id=notice_id)
        
        # Check if user has permission to view this notice
        if notice.audience == 'staff' and request.user.role == 'student':
            return Response(
                {'error': 'You do not have permission to view this notice.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = NoticeSerializer(notice)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Notice.DoesNotExist:
        return Response(
            {'error': 'Notice not found.'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_notice_view(request, notice_id):
    """
    Update or delete a notice (Admin only)
    PUT/PATCH /api/notices/<notice_id>/
    DELETE /api/notices/<notice_id>/
    """
    # Check if user has permission (admin only)
    if request.user.role != 'admin':
        return Response(
            {'error': 'Only admins can manage notices.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        notice = Notice.objects.get(id=notice_id)
    except Notice.DoesNotExist:
        return Response(
            {'error': 'Notice not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method in ['PUT', 'PATCH']:
        # For partial updates, use partial=True
        partial = request.method == 'PATCH'
        serializer = NoticeCreateSerializer(
            notice, 
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
            updated_notice = serializer.save()
            return Response({
                'message': 'Notice updated successfully',
                'notice': NoticeSerializer(updated_notice).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Failed to update notice: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    elif request.method == 'DELETE':
        try:
            notice.delete()
            return Response(
                {'message': 'Notice deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to delete notice: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )