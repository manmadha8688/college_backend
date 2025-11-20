from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from .models import User, Student, Staff, HeadOfDepartment


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details"""
    full_name = serializers.SerializerMethodField()
    student_profile = serializers.SerializerMethodField()
    staff_profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'full_name', 
                  'role', 'date_joined', 'is_active', 'student_profile', 'staff_profile')
        read_only_fields = ('id', 'date_joined', 'is_active', 'role')
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_student_profile(self, obj):
        """Return student profile without circular reference"""
        if hasattr(obj, 'student_profile'):
            student = obj.student_profile
            return {
                'student_id': student.student_id,
                'date_of_birth': student.date_of_birth,
                'gender': student.gender,
                'phone': student.phone,
                'address': student.address,
                'enrollment_date': student.enrollment_date,
                'department': student.department,
            }
        return None
    
    def get_staff_profile(self, obj):
        """Return staff profile without circular reference"""
        if hasattr(obj, 'staff_profile'):
            staff = obj.staff_profile
            return {
                'staff_id': staff.staff_id,
                'date_of_birth': staff.date_of_birth,
                'gender': staff.gender,
                'phone': staff.phone,
                'address': staff.address,
                'department': staff.department,
                'designation': staff.designation,
                'qualification': staff.qualification,
                'joining_date': staff.joining_date,
                'salary': str(staff.salary) if staff.salary else None,
            }
        return None


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for Student model"""
    user = serializers.SerializerMethodField()
    email = serializers.EmailField(write_only=True, required=False)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    user_email = serializers.EmailField(write_only=True, required=False)
    user_first_name = serializers.CharField(write_only=True, required=False)
    user_last_name = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Student
        fields = (
            'user', 'student_id', 'date_of_birth', 'gender', 'phone', 
            'address', 'enrollment_date', 'department', 'created_at', 'updated_at',
            'email', 'first_name', 'last_name',
            'user_email', 'user_first_name', 'user_last_name'
        )
        read_only_fields = ('user', 'enrollment_date', 'created_at', 'updated_at')
    
    def get_user(self, obj):
        """Return user details without circular reference"""
        if obj.user:
            return {
                'id': obj.user.id,
                'email': obj.user.email,
                'first_name': obj.user.first_name,
                'last_name': obj.user.last_name,
                'full_name': obj.user.get_full_name(),
                'role': obj.user.role,
                'is_active': obj.user.is_active
            }
        return None
    
    def update(self, instance, validated_data):
        """Update student and related user"""
        # Handle user fields - extract email, first_name, last_name
        user_data = {}
        
        # Check for direct email/first_name/last_name fields
        if 'email' in validated_data:
            user_data['email'] = validated_data.pop('email')
        if 'first_name' in validated_data:
            user_data['first_name'] = validated_data.pop('first_name')
        if 'last_name' in validated_data:
            user_data['last_name'] = validated_data.pop('last_name')
        
        # Check for user_email/user_first_name/user_last_name fields (backward compatibility)
        if 'user_email' in validated_data:
            user_data['email'] = validated_data.pop('user_email')
        if 'user_first_name' in validated_data:
            user_data['first_name'] = validated_data.pop('user_first_name')
        if 'user_last_name' in validated_data:
            user_data['last_name'] = validated_data.pop('user_last_name')
        
        # Handle department field specifically to ensure case sensitivity and validity
        if 'department' in validated_data:
            dept = validated_data['department']
            if dept:
                # Convert to uppercase to match choices
                dept = dept.upper()
                # Check if the department is in the valid choices
                valid_departments = dict(instance.DEPARTMENT_CHOICES).keys()
                if dept not in valid_departments:
                    raise serializers.ValidationError({
                        'department': f'"{dept}" is not a valid department. Must be one of: {list(valid_departments)}'
                    })
                validated_data['department'] = dept
        
        # Update User model if user data is provided
        if user_data and instance.user:
            user = instance.user
            for key, value in user_data.items():
                if value or value == '':  # Update even if empty string (to allow clearing)
                    setattr(user, key, value if value else '')
            user.save()
        
        # Update Student model
        for attr, value in validated_data.items():
            # Skip empty strings for optional fields, convert to None
            if value == '' and attr in ['date_of_birth', 'gender', 'phone', 'address', 'department']:
                setattr(instance, attr, None)
            else:
                setattr(instance, attr, value)
        
        try:
            instance.save()
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
        return instance


class StaffSerializer(serializers.ModelSerializer):
    """Serializer for Staff model"""
    user = serializers.SerializerMethodField()
    email = serializers.EmailField(write_only=True, required=False)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    user_email = serializers.EmailField(write_only=True, required=False)
    user_first_name = serializers.CharField(write_only=True, required=False)
    user_last_name = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Staff
        fields = (
            'user', 'staff_id', 'date_of_birth', 'gender', 'phone', 
            'address', 'department', 'designation', 'qualification', 
            'joining_date', 'salary', 'created_at', 'updated_at',
            'email', 'first_name', 'last_name',
            'user_email', 'user_first_name', 'user_last_name'
        )
        read_only_fields = ('user', 'joining_date', 'created_at', 'updated_at')
    
    def get_user(self, obj):
        """Return user details without circular reference"""
        if obj.user:
            return {
                'id': obj.user.id,
                'email': obj.user.email,
                'first_name': obj.user.first_name,
                'last_name': obj.user.last_name,
                'full_name': obj.user.get_full_name(),
                'role': obj.user.role,
                'is_active': obj.user.is_active  # Add this line
            }
        return None
    
    def update(self, instance, validated_data):
        """Update staff and related user"""
        # Handle user fields - extract email, first_name, last_name
        user_data = {}
        
        # Check for direct email/first_name/last_name fields
        if 'email' in validated_data:
            user_data['email'] = validated_data.pop('email')
        if 'first_name' in validated_data:
            user_data['first_name'] = validated_data.pop('first_name')
        if 'last_name' in validated_data:
            user_data['last_name'] = validated_data.pop('last_name')
        
        # Check for user_email/user_first_name/user_last_name fields (backward compatibility)
        if 'user_email' in validated_data:
            user_data['email'] = validated_data.pop('user_email')
        if 'user_first_name' in validated_data:
            user_data['first_name'] = validated_data.pop('user_first_name')
        if 'user_last_name' in validated_data:
            user_data['last_name'] = validated_data.pop('user_last_name')
        
        # Update User model if user data is provided
        if user_data and instance.user:
            user = instance.user
            for key, value in user_data.items():
                if value or value == '':  # Update even if empty string (to allow clearing)
                    setattr(user, key, value if value else '')
            user.save()
        
        # Update Staff model
        for attr, value in validated_data.items():
            # Skip empty strings for optional fields, convert to None
            if value == '' and attr in ['date_of_birth', 'gender', 'phone', 'address', 'department', 
                                      'designation', 'qualification', 'salary']:
                setattr(instance, attr, None)
            else:
                setattr(instance, attr, value)
        instance.save()
        
        return instance


class StudentRegistrationSerializer(serializers.Serializer):
    """Serializer for creating a student with user account"""
    # User fields
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True, max_length=100)
    last_name = serializers.CharField(required=True, max_length=100)
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        label="Confirm Password"
    )
    
    # Student fields
    student_id = serializers.CharField(required=True, max_length=50)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    gender = serializers.ChoiceField(choices=Student.GENDER_CHOICES, required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=15)
    address = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    department = serializers.ChoiceField(choices=Student.DEPARTMENT_CHOICES, required=False, allow_null=True)
    
    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        
        # Check if email already exists
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError(
                {"email": "A user with this email already exists."}
            )
        
        # Check if student_id already exists
        if Student.objects.filter(student_id=attrs['student_id']).exists():
            raise serializers.ValidationError(
                {"student_id": "A student with this ID already exists."}
            )
        
        # Convert empty strings to None for optional fields
        for field in ['date_of_birth', 'gender', 'phone', 'address', 'department']:
            if field in attrs and attrs[field] == '':
                attrs[field] = None
        
        return attrs
    
    def create(self, validated_data):
        """Create a new student with user account"""
        password = validated_data.pop('password')
        validated_data.pop('password2')
        
        # Extract student-specific data
        student_id = validated_data.pop('student_id')
        date_of_birth = validated_data.pop('date_of_birth', None)
        gender = validated_data.pop('gender', None)
        phone = validated_data.pop('phone', None)
        address = validated_data.pop('address', None)
        department = validated_data.pop('department', None)
        
        # Create user
        user = User.objects.create_user(
            password=password,
            role='student',
            **validated_data
        )
        
        # Create student profile
        student = Student.objects.create(
            user=user,
            student_id=student_id,
            date_of_birth=date_of_birth,
            gender=gender,
            phone=phone,
            address=address,
            department=department
        )
        
        return student


class StaffRegistrationSerializer(serializers.Serializer):
    """Serializer for creating a staff member with user account"""
    # User fields
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True, max_length=100)
    last_name = serializers.CharField(required=True, max_length=100)
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        label="Confirm Password"
    )
    
    # Staff fields
    staff_id = serializers.CharField(required=True, max_length=50)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    gender = serializers.ChoiceField(choices=Staff.GENDER_CHOICES, required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=15)
    address = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    department = serializers.ChoiceField(choices=Staff.DEPARTMENT_CHOICES, required=False, allow_null=True)
    designation = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=100)
    qualification = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=200)
    salary = serializers.DecimalField(required=False, allow_null=True, max_digits=10, decimal_places=2)
    
    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        
        # Check if email already exists
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError(
                {"email": "A user with this email already exists."}
            )
        
        # Check if staff_id already exists
        if Staff.objects.filter(staff_id=attrs['staff_id']).exists():
            raise serializers.ValidationError(
                {"staff_id": "A staff member with this ID already exists."}
            )
        
        # Convert empty strings to None for optional fields
        for field in ['date_of_birth', 'gender', 'phone', 'address', 'department', 
                     'designation', 'qualification', 'salary']:
            if field in attrs and attrs[field] == '':
                attrs[field] = None
        
        return attrs
    
    def create(self, validated_data):
        """Create a new staff member with user account"""
        password = validated_data.pop('password')
        validated_data.pop('password2')
        
        # Extract staff-specific data
        staff_id = validated_data.pop('staff_id')
        date_of_birth = validated_data.pop('date_of_birth', None)
        gender = validated_data.pop('gender', None)
        phone = validated_data.pop('phone', None)
        address = validated_data.pop('address', None)
        department = validated_data.pop('department', None)
        designation = validated_data.pop('designation', None)
        qualification = validated_data.pop('qualification', None)
        salary = validated_data.pop('salary', None)
        
        # Create user
        user = User.objects.create_user(
            password=password,
            role='staff',
            is_staff=True,
            **validated_data
        )
        
        # Create staff profile
        staff = Staff.objects.create(
            user=user,
            staff_id=staff_id,
            date_of_birth=date_of_birth,
            gender=gender,
            phone=phone,
            address=address,
            department=department,
            designation=designation,
            qualification=qualification,
            salary=salary
        )
        
        return staff


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for basic user registration (admin only)"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        label="Confirm Password"
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role', 'password', 'password2')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'role': {'required': True},
        }
    
    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        
        return attrs
    
    def create(self, validated_data):
        """Create a new user"""
        validated_data.pop('password2')
        password = validated_data.pop('password')
        
        # Set is_staff based on role
        if validated_data.get('role') in ['admin', 'staff']:
            validated_data['is_staff'] = True
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class HeadOfDepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Head of Department model"""
    staff_id = serializers.CharField(source='staff.staff_id', read_only=True)
    staff_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    
    class Meta:
        model = HeadOfDepartment
        fields = (
            'id', 'staff', 'staff_id', 'staff_name', 'department', 'department_name',
            'start_date', 'end_date', 'is_active', 'additional_responsibilities',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'staff_id', 'staff_name', 'department_name')
    
    def get_staff_name(self, obj):
        """Get the full name of the staff member"""
        return obj.staff.user.get_full_name()
    
    def get_department_name(self, obj):
        """Get the display name of the department"""
        return obj.get_department_display()
    
    def validate(self, attrs):
        """Validate the HOD appointment"""
        staff = attrs.get('staff')
        department = attrs.get('department')
        
        # Check if staff exists and is active
        if not staff.user.is_active:
            raise serializers.ValidationError("Cannot assign an inactive staff member as HOD.")
        
        # Check if staff is already HOD of another department
        existing_hod = HeadOfDepartment.objects.filter(
            staff=staff,
            is_active=True
        ).exclude(pk=self.instance.pk if self.instance else None).first()
        
        if existing_hod:
            raise serializers.ValidationError(
                f"This staff member is already the HOD of {existing_hod.get_department_display()} department."
            )
        
        # Check if there's already an active HOD for this department
        existing_dept_hod = HeadOfDepartment.objects.filter(
            department=department,
            is_active=True
        ).exclude(pk=self.instance.pk if self.instance else None).first()
        
        if existing_dept_hod:
            raise serializers.ValidationError(
                f"{existing_dept_hod.staff.user.get_full_name()} is already the HOD of {existing_dept_hod.get_department_display()} department."
            )
        
        return attrs
    
    def create(self, validated_data):
        """Create a new HOD appointment"""
        # End any existing active HOD for this department
        HeadOfDepartment.objects.filter(
            department=validated_data['department'],
            is_active=True
        ).update(is_active=False, end_date=timezone.now().date())
        
        # Set start date to current date if not provided
        if 'start_date' not in validated_data:
            validated_data['start_date'] = timezone.now().date()
            
        # Create new HOD appointment
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update HOD appointment"""
        # If department is being changed, end the current HOD's term
        if 'department' in validated_data and instance.department != validated_data['department']:
            instance.end_date = timezone.now().date()
            instance.is_active = False
            instance.save()
            
            # Create a new HOD record for the new department
            validated_data.pop('start_date', None)  # Use current date for new appointment
            return super().create(validated_data)
            
        return super().update(instance, validated_data)
