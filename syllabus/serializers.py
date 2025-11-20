from rest_framework import serializers
from .models import Subject, Syllabus

class SyllabusSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.subject_code', read_only=True)
    department = serializers.CharField(source='subject.department', read_only=True)
    semester = serializers.IntegerField(source='subject.semester', read_only=True)
    
    class Meta:
        model = Syllabus
        fields = ['id', 'subject', 'subject_name', 'subject_code', 'department', 
                 'semester', 'pdf_url', 'uploaded_at']
        read_only_fields = ['uploaded_at', 'subject']

class SubjectSerializer(serializers.ModelSerializer):
    syllabus = SyllabusSerializer(read_only=True)
    pdf_url = serializers.URLField(write_only=True, required=False, allow_null=True, allow_blank=True)
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'subject_code', 'department', 'semester', 'syllabus', 'pdf_url']
        read_only_fields = ['subject_code']
    
    def create(self, validated_data):
        pdf_url = validated_data.pop('pdf_url', None)
        subject = Subject.objects.create(**validated_data)
        
        # Only create syllabus if pdf_url is provided and not empty
        if pdf_url:
            Syllabus.objects.create(subject=subject, pdf_url=pdf_url)
            
        return subject
