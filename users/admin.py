from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Student, Staff


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model"""
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin interface for Student model"""
    list_display = ('student_id', 'user', 'department', 'enrollment_date')
    list_filter = ('department', 'gender', 'enrollment_date')
    search_fields = ('student_id', 'user__email', 'user__first_name', 'user__last_name', 'department')
    ordering = ('-enrollment_date',)
    readonly_fields = ('created_at', 'updated_at', 'enrollment_date')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'student_id')
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'gender', 'phone', 'address')
        }),
        ('Academic Information', {
            'fields': ('department', 'enrollment_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    """Admin interface for Staff model"""
    list_display = ('staff_id', 'user', 'department', 'designation', 'joining_date')
    list_filter = ('department', 'designation', 'gender', 'joining_date')
    search_fields = ('staff_id', 'user__email', 'user__first_name', 'user__last_name', 'department', 'designation')
    ordering = ('-joining_date',)
    readonly_fields = ('created_at', 'updated_at', 'joining_date')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'staff_id')
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'gender', 'phone', 'address')
        }),
        ('Professional Information', {
            'fields': ('department', 'designation', 'qualification', 'joining_date', 'salary')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
