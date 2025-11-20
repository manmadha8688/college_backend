from django.db import models
from django.db.models import Max

DEPARTMENT_CHOICES = [
    ("CS", "Computer Science & Engineering"),
    ("ECE", "Electronics & Communication Engineering"),
    ("EE", "Electrical & Electronics Engineering"),
    ("MECH", "Mechanical Engineering"),
    ("CIVIL", "Civil Engineering"),
    ("IT", "Information Technology"),
]

SEMESTER_CHOICES = [(i, f"Semester {i}") for i in range(1, 9)]


class Subject(models.Model):
    name = models.CharField(max_length=150)
    subject_code = models.CharField(
        max_length=10,
        unique=True,
        editable=False,  # Make it non-editable in admin
        help_text="Auto-generated code in format: {dept}{semester}{number} (e.g., CSE1101)"
    )
    department = models.CharField(max_length=10, choices=DEPARTMENT_CHOICES)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    
    def generate_subject_code(self):
        """Generate subject code in format: {dept}{semester}{2-digit-number}"""
        # Get department code (first 2-3 letters)
        dept_code = self.department.upper()
        
        # Get the next sequence number for this department + semester
        last_subject = Subject.objects.filter(
            department=self.department,
            semester=self.semester
        ).order_by('-subject_code').first()
        
        if last_subject and last_subject.subject_code:
            # Extract the last sequence number and increment
            last_code = last_subject.subject_code
            try:
                # Extract the numeric part after department and semester
                seq_num = int(last_code[len(dept_code) + 1:]) + 1
            except (ValueError, IndexError):
                seq_num = 1
        else:
            seq_num = 1
            
        # Format the code: CSE1101, CSE1102, etc.
        return f"{dept_code}{self.semester}{seq_num:02d}"
    
    def save(self, *args, **kwargs):
        if not self.subject_code:  # Only generate code if it doesn't exist
            self.subject_code = self.generate_subject_code()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ("name", "department", "semester")
        ordering = ['department', 'semester', 'name']

    def __str__(self):
        return f"{self.name} - {self.department} - Sem {self.semester}"


class Syllabus(models.Model):
    subject = models.OneToOneField(Subject, on_delete=models.CASCADE)
    pdf_url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Syllabus for {self.subject.name}"
