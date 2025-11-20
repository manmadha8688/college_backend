from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    """Custom user manager for handling user creation"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model for college portal"""
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('student', 'Student'),
    ]
    
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.email} ({self.role})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.first_name


class Student(models.Model):
    """Student model with OneToOne relationship to User"""

    DEPARTMENT_CHOICES = [
        ('IT', 'Information Technology'),
        ('CS', 'Computer Science'),
        ('EE', 'Electrical Engineering'),
        ('ME', 'Mechanical Engineering'),
        ('CE', 'Civil Engineering'),
        ('ADMIN', 'Administration'),
        ('ACCOUNTS', 'Accounts'),
        ('LIBRARY', 'Library'),
        ('OTHER', 'Other'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        primary_key=True
    )
    student_id = models.CharField(
        max_length=50,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9]+$',
                message='Student ID must contain only uppercase letters and numbers.'
            )
        ],
        help_text='Unique student identification number'
    )
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    phone = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.'
            )
        ]
    )
    address = models.TextField(null=True, blank=True)
    enrollment_date = models.DateField(auto_now_add=True)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'students'
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        ordering = ['-enrollment_date']
    
    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        # Ensure user role is set to student
        if self.user and self.user.role != 'student':
            self.user.role = 'student'
            self.user.save(update_fields=['role'])
        super().save(*args, **kwargs)


class Staff(models.Model):
    """Staff model with OneToOne relationship to User"""
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    DEPARTMENT_CHOICES = [
        ('IT', 'Information Technology'),
        ('CS', 'Computer Science'),
        ('EE', 'Electrical Engineering'),
        ('ME', 'Mechanical Engineering'),
        ('CE', 'Civil Engineering'),
        ('ADMIN', 'Administration'),
        ('ACCOUNTS', 'Accounts'),
        ('LIBRARY', 'Library'),
        ('OTHER', 'Other'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='staff_profile',
        primary_key=True
    )
    staff_id = models.CharField(
        max_length=50,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9]+$',
                message='Staff ID must contain only uppercase letters and numbers.'
            )
        ],
        help_text='Unique staff identification number'
    )
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    phone = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.'
            )
        ]
    )
    address = models.TextField(null=True, blank=True)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True, help_text='e.g., Professor, Assistant Professor, Lab Assistant')
    qualification = models.CharField(max_length=200, null=True, blank=True)
    joining_date = models.DateField(auto_now_add=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'staff'
        verbose_name = 'Staff'
        verbose_name_plural = 'Staff'
        ordering = ['-joining_date']


class HeadOfDepartment(models.Model):
    """
    Model to track Heads of Departments (HODs).
    Each department can have only one active HOD at a time.
    """
    
    staff = models.OneToOneField(
        Staff,
        on_delete=models.CASCADE,
        related_name='hod_role',
        help_text='Staff member who is the Head of Department'
    )
    
    department = models.CharField(
        max_length=50,
        choices=Staff.DEPARTMENT_CHOICES,
        help_text='Department for which this staff is the HOD'
    )
    
    start_date = models.DateField(
        help_text='Date when the staff member became HOD of this department'
    )
    
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date when the staff member stopped being HOD (if applicable)'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this HOD assignment is currently active'
    )
    
    additional_responsibilities = models.TextField(
        null=True,
        blank=True,
        help_text='Any additional responsibilities or notes for this HOD role'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'head_of_department'
        verbose_name = 'Head of Department'
        verbose_name_plural = 'Heads of Department'
        ordering = ['department', '-start_date']
        constraints = [
            models.UniqueConstraint(
                fields=['department', 'is_active'],
                condition=models.Q(is_active=True),
                name='unique_active_hod_per_department'
            )
        ]
    
    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.get_department_display()} (HOD)"
    
    def save(self, *args, **kwargs):
        # If this is a new active HOD assignment, deactivate any existing active HOD for this department
        if self.is_active and not self.pk:
            HeadOfDepartment.objects.filter(
                department=self.department,
                is_active=True
            ).exclude(pk=self.pk).update(is_active=False)
        
        # If this HOD is being marked as inactive, ensure end_date is set
        if not self.is_active and not self.end_date:
            self.end_date = timezone.now().date()
        
        # Ensure the staff's user has the correct role
        if self.staff and self.staff.user and self.staff.user.role != 'staff':
            self.staff.user.role = 'staff'
            self.staff.user.save(update_fields=['role'])
        
        super().save(*args, **kwargs)
    
    @property
    def duration(self):
        """Calculate the duration of the HOD role"""
        end = self.end_date if self.end_date else timezone.now().date()
        return (end - self.start_date).days
