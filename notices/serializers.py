from rest_framework import serializers
from .models import Notice


class NoticeSerializer(serializers.ModelSerializer):
    """Serializer for Notice model"""
    posted_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Notice
        fields = (
            'id', 'category', 'audience', 'title', 'content', 
            'date', 'datetime', 'priority', 'expiry_date',
            'posted_by', 'posted_by_name', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'posted_by', 'created_at', 'updated_at')
    
    def get_posted_by_name(self, obj):
        if obj.posted_by:
            return obj.posted_by.get_full_name()
        return None


class NoticeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a notice"""
    
    class Meta:
        model = Notice
        fields = (
            'category', 'audience', 'title', 'content',
            'date', 'datetime', 'priority', 'expiry_date'
        )
    
    def validate(self, attrs):
        # Convert empty strings to None for optional fields
        for field in ['title', 'content', 'date', 'datetime', 'expiry_date']:
            if field in attrs and attrs[field] == '':
                attrs[field] = None
        
        # Validate that at least title or content is provided
        if not attrs.get('title') and not attrs.get('content'):
            raise serializers.ValidationError(
                {'title': 'Either title or content must be provided.'}
            )
        
        # If audience is not provided, it will be auto-set in the model's save method
        # But we can validate it here if provided
        category = attrs.get('category')
        audience = attrs.get('audience')
        
        if category:
            staff_categories = [
                'Staff Meeting', 'Invigilation Duty', 'Internal Circular', 'Timetable Work',
                'Leave / Policy Update', 'Faculty Training', 'Research Opportunities',
                'Staff Achievements', 'Maintenance Notices', 'IT & System Updates'
            ]
            all_users_categories = [
                'Holiday Announcement', 'Exam Timetable', 'Events', 'Results', 'Fee Notices',
                'Emergency Alerts', 'Workshops / Seminars', 'Scholarship / Grants',
                'Campus News', 'Sports / Cultural Updates'
            ]
            
            # Auto-set audience if not provided
            if not audience:
                if category in staff_categories:
                    attrs['audience'] = 'staff'
                elif category in all_users_categories:
                    attrs['audience'] = 'all'
        
        return attrs
    
    def create(self, validated_data):
        # Set the posted_by to the current user
        validated_data['posted_by'] = self.context['request'].user
        return super().create(validated_data)

