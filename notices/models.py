from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notice(models.Model):

    # ---------------- CATEGORY ----------------
    CATEGORY_CHOICES = [
        # Staff Categories
        ('Staff Meeting', 'Staff Meeting'),
        ('Invigilation Duty', 'Invigilation Duty'),
        ('Internal Circular', 'Internal Circular'),
        ('Timetable Work', 'Timetable Work'),
        ('Leave / Policy Update', 'Leave / Policy Update'),
        ('Faculty Training', 'Faculty Training'),
        ('Research Opportunities', 'Research Opportunities'),
        ('Staff Achievements', 'Staff Achievements'),
        ('Maintenance Notices', 'Maintenance Notices'),
        ('IT & System Updates', 'IT & System Updates'),

        # All Users Categories
        ('Holiday Announcement', 'Holiday Announcement'),
        ('Exam Timetable', 'Exam Timetable'),
        ('Events', 'Events'),
        ('Results', 'Results'),
        ('Fee Notices', 'Fee Notices'),
        ('Emergency Alerts', 'Emergency Alerts'),
        ('Workshops / Seminars', 'Workshops / Seminars'),
        ('Scholarship / Grants', 'Scholarship / Grants'),
        ('Campus News', 'Campus News'),
        ('Sports / Cultural Updates', 'Sports / Cultural Updates'),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    # ---------------- AUDIENCE ----------------
    AUDIENCE_CHOICES = [
        ('staff', 'Staff Only'),
        ('all', 'All Users'),
    ]
    audience = models.CharField(max_length=10, choices=AUDIENCE_CHOICES)

    # ---------------- FIELDS ----------------
    title = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)          # For holidays, exams, deadlines
    datetime = models.DateTimeField(blank=True, null=True)  # For meetings, trainings

    # ---------------- OPTIONAL ----------------
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.CharField(
        max_length=10,
        choices=[('normal', 'Normal'), ('important', 'Important'), ('urgent', 'Urgent')],
        default='normal'
    )
    expiry_date = models.DateTimeField(blank=True, null=True)  # Optional auto-hide

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Automatically set audience based on category if not manually set
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

        if not self.audience:
            if self.category in staff_categories:
                self.audience = 'staff'
            elif self.category in all_users_categories:
                self.audience = 'all'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category} - {self.title or 'No Title'}"
