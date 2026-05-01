from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from accounts.utils import extract_and_save_pdf_content
from core import settings
from django.db.models.signals import post_save

# ===============================
# USER MANAGER
# ===============================

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role='CADET', **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            role=role,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(
            email=email,
            password=password,
            role='ADMIN',
            **extra_fields
        )

        user.is_staff = True
        user.is_superuser = True
        user.is_approved = True
        user.save(using=self._db)
        return user


# ===============================
# USER MODEL (AUTH ONLY)
# ===============================

class User(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('OFFICER', 'Officer'),
        ('CADET', 'Cadet'),
    )

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CADET')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    profile_completed = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email


# ===============================
# CADET PROFILE (NCC CORE)
# ===============================

class CadetProfile(models.Model):

    WING_CHOICES = (
        ('ARMY', 'Army'),
        ('NAVY', 'Navy'),
        ('AIR', 'Air'),
    )

    DIVISION_CHOICES = (
        ('SD', 'Senior Division'),
        ('SW', 'Senior Wing'),
        ('JD', 'Junior Division'),
        ('JW', 'Junior Wing'),
    )

    BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cadet_profile')

    cadet_number = models.CharField(max_length=50, unique=True)
    wing = models.CharField(max_length=10, choices=WING_CHOICES)
    division = models.CharField(max_length=5, choices=DIVISION_CHOICES)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)
    training_year = models.IntegerField(null=True, blank=True)

    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

    previously_in_ncc = models.BooleanField(default=False)
    previous_ncc_institution = models.CharField(max_length=200, null=True, blank=True)
    previous_ncc_certificate = models.CharField(max_length=50, null=True, blank=True)


    # ====================================
    # 🔐 EDIT CONTROL SYSTEM
    # ====================================

    profile_editable_until = models.DateTimeField(
        default=timezone.now() + timedelta(days=10)
    )

    edit_permission_granted = models.BooleanField(default=False)

    correction_requested = models.BooleanField(default=False)

    # ====================================
    # EDIT LOGIC
    # ====================================

    def can_edit(self):
        return (
            timezone.now() <= self.profile_editable_until
            or self.edit_permission_granted
        )


    def __str__(self):
        return f"{self.user.name} - {self.cadet_number}"


# ===============================
# PERSONAL DETAILS
# ===============================

class PersonalDetails(models.Model):

    GENDER_CHOICES = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='personal_details')

    date_of_birth = models.DateField(null=True,blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    address = models.TextField()
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    religion = models.CharField(max_length=100)
    caste = models.CharField(max_length=100)
    identification_mark = models.TextField()

    parent_name = models.CharField(max_length=150)
    emergency_contact_name = models.CharField(max_length=150)
    emergency_contact_number = models.CharField(max_length=15)

    def __str__(self):
        return f"Personal Details - {self.user.name}"


# ===============================
# ACADEMIC DETAILS
# ===============================

class AcademicDetails(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='academic_details')

    admission_number = models.CharField(max_length=50, unique=True)
    university_register_number = models.CharField(max_length=50, unique=True)

    course = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    semester = models.IntegerField()
    year_of_joining = models.IntegerField()

    def __str__(self):
        return f"Academic Details - {self.user.name}"


# ===============================
# BANK DETAILS
# ===============================

class BankDetails(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='bank_details')

    account_holder_name = models.CharField(max_length=150)
    account_number = models.CharField(max_length=30)
    bank_name = models.CharField(max_length=100)
    branch = models.CharField(max_length=100)
    ifsc_code = models.CharField(max_length=20)

    def __str__(self):
        return f"Bank Details - {self.user.name}"


# ===============================
# IDENTITY DETAILS
# ===============================

class IdentityDetails(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='identity_details')

    aadhaar_number = models.CharField(max_length=12)
    pan_number = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"Identity Details - {self.user.name}"


# ===============================
# MEDICAL DETAILS
# ===============================

class MedicalDetails(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='medical_details')

    height_cm = models.DecimalField(max_digits=5, decimal_places=2)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2)

    chest_normal_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    chest_expanded_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    medical_conditions = models.TextField(null=True, blank=True)
    medically_fit = models.BooleanField(default=True)

    def __str__(self):
        return f"Medical Details - {self.user.name}"


# ===============================
# DOCUMENT UPLOADS
# ===============================

class Document(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='official_documents')

    document_type = models.CharField(max_length=100)
    file = models.FileField(upload_to='documents/')

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document_type} - {self.user.name}"


# ===============================
# ACTIVITY MODEL
# ===============================

class Activity(models.Model):

    ACTIVITY_TYPE_CHOICES = (
        ('CAMP', 'Camp'),
        ('OFFICIAL_PARADE', 'Official Parade'),
        ('UNOFFICIAL_PARADE', 'Unofficial Parade'),
        ('EVENT', 'Event'),
    )

    title = models.CharField(max_length=200)

    activity_type = models.CharField(
        max_length=30,
        choices=ACTIVITY_TYPE_CHOICES
    )

    date = models.DateField()

    location = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'OFFICER'}
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.date}"
    
# ===============================
# ATTENDANCE MODEL
# ===============================

class Attendance(models.Model):

    STATUS_CHOICES = (
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
    )

    cadet = models.ForeignKey(
        CadetProfile,
        on_delete=models.CASCADE,
        related_name='attendances'
    )

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='attendances'
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
    )

    marked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='marked_attendance'
    )

    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cadet', 'activity')

    def __str__(self):
        return f"{self.cadet.user.email} - {self.activity.title}"

# ===============================
# CAMP MODEL
# ===============================

class Camp(models.Model):

    CAMP_TYPE_CHOICES = (
        ('ATC', 'Annual Training Camp'),
        ('CATC', 'Combined Annual Training Camp'),
        ('NIC', 'National Integration Camp'),
        ('TSC', 'Thal Sainik Camp'),
        ('RDC', 'Republic Day Camp'),
        ('ADVENTUROUS CAMP', 'Adventurous Camp'),
        ('TREKKING', 'Trekking Camp'),
        ('EBSB','EBSB')

    )

    title = models.CharField(max_length=200)
    total_seats = models.PositiveIntegerField(null=True,blank=True)

    camp_type = models.CharField(
        max_length=50,
        choices=CAMP_TYPE_CHOICES
    )

    location = models.CharField(max_length=200)

    start_date = models.DateField()
    end_date = models.DateField()

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'OFFICER'}
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def approved_count(self):
        return self.participants.filter(status="APPROVED").count()

    def seats_left(self):
        return self.total_seats - self.approved_count()

    def __str__(self):
        return f"{self.title} ({self.start_date})"
    
# ===============================
# CAMP PARTICIPATION
# ===============================

class CampParticipation(models.Model):

    STATUS_CHOICES = (
        ('APPLIED', 'Applied'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
    )

    cadet = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'CADET'}
    )

    camp = models.ForeignKey(
        Camp,
        on_delete=models.CASCADE,
        related_name='participants'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='APPLIED'
    )

    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cadet', 'camp')

    def __str__(self):
        return f"{self.cadet.name} - {self.camp.title}"
    
# ===============================
# EVENT MODEL
# ===============================

class Event(models.Model):

    EVENT_TYPE_CHOICES = (
        ('PARADE_OFFICIAL', 'Official Parade'),
        ('PARADE_UNOFFICIAL', 'Unofficial Parade'),
        ('SEMINAR', 'Seminar'),
        ('SOCIAL_ACTIVITY', 'Social Activity'),
        ('COMPETITION', 'Competition'),
    )

    title = models.CharField(max_length=200)

    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPE_CHOICES
    )

    date = models.DateField()
    location = models.CharField(max_length=200)

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'OFFICER'}
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.date}"

# ===============================
# EVENT PARTICIPATION
# ===============================

class EventParticipation(models.Model):

    cadet = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'CADET'}
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='participants'
    )

    attended = models.BooleanField(default=False)

    class Meta:
        unique_together = ('cadet', 'event')

    def __str__(self):
        return f"{self.cadet.name} - {self.event.title}"

# ===============================
# NOTICE BOARD
# ===============================
# ===============================
# NOTICE BOARD MODEL
# ===============================

class Notice(models.Model):

    PRIORITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    )

    TARGET_CHOICES = (
        ('ALL', 'All Users'),
        ('CADET', 'Cadets Only'),
        ('OFFICER', 'Officers Only'),
    )

    title = models.CharField(max_length=200)

    message = models.TextField()

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='LOW'
    )

    target_role = models.CharField(
        max_length=20,
        choices=TARGET_CHOICES,
        default='ALL'
    )

    attachment = models.FileField(
        upload_to='notice_attachments/',
        null=True,
        blank=True
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role__in': ['ADMIN', 'OFFICER']}
    )

    is_active = models.BooleanField(default=True)

    expiry_date = models.DateField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

# ===============================
# DOCUMENT MODEL
# ===============================

class CadetDocument(models.Model):

    DOCUMENT_TYPE_CHOICES = (
        ('AADHAAR', 'Aadhaar'),
        ('BANK_PROOF', 'Bank Proof'),
        ('MEDICAL', 'Medical Certificate'),
        ('CAMP_FORM', 'Camp Application Form'),
        ('OTHER', 'Other'),
    )

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    cadet = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'CADET'},
        related_name='cadet_documents'
    )

    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES
    )

    file = models.FileField(
        upload_to='cadet_documents/'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents'
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True
    )

    remarks = models.TextField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.cadet.name} - {self.document_type}"

# ===============================
# CERTIFICATE MODEL
# ===============================

class Certificate(models.Model):

    CERTIFICATE_TYPE_CHOICES = (
        ('CAMP', 'Camp Certificate'),
        ('EVENT', 'Event Certificate'),
        ('ACHIEVEMENT', 'Achievement Certificate'),
    )

    cadet = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'CADET'},
        related_name='certificates'
    )

    certificate_type = models.CharField(
        max_length=50,
        choices=CERTIFICATE_TYPE_CHOICES
    )

    title = models.CharField(max_length=200)

    file = models.FileField(
        upload_to='certificates/'
    )

    issued_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role__in': ['ADMIN', 'OFFICER']}
    )

    issued_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cadet.name} - {self.title}"

# ===============================
# FEEDBACK MODEL
# ===============================

class Feedback(models.Model):

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('RESOLVED', 'Resolved'),
        ('REJECTED', 'Rejected'),
    )

    cadet = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'CADET'},
        related_name='feedbacks'
    )

    subject = models.CharField(max_length=200)
    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    response = models.TextField(blank=True, null=True)

    responded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedback_responses'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.cadet.name} - {self.subject}"

# ===============================
# POLL MODEL
# ===============================

class Poll(models.Model):

    question = models.CharField(max_length=300)

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role__in': ['ADMIN', 'OFFICER']}
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.question
    
class PollOption(models.Model):

    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='options'
    )

    option_text = models.CharField(max_length=200)

    def __str__(self):
        return self.option_text

class PollVote(models.Model):

    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE)

    cadet = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'CADET'}
    )

    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('poll', 'cadet')

# ===============================
# NOTIFICATION MODEL
# ===============================

class Notification(models.Model):

    NOTIFICATION_TYPE_CHOICES = (
        ('NOTICE', 'Notice'),
        ('EVENT', 'Event'),
        ('ATTENDANCE', 'Attendance'),
        ('GENERAL', 'General'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    title = models.CharField(max_length=200)
    message = models.TextField()

    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPE_CHOICES
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    group_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.title}"




# ===============================
# QR ATTENDANCE SESSION
# ===============================

import uuid


class QRAttendanceSession(models.Model):
    activity = models.ForeignKey(
        'Activity', # Ensure Activity model is defined above or imported
        on_delete=models.CASCADE,
        related_name='qr_sessions'
    )

    # Using UUID makes the QR URL impossible to "guess" by changing numbers
    qr_code = models.CharField(max_length=255, unique=True, default=uuid.uuid4)

    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField()

    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        'User', 
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'OFFICER'}
    )

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_currently_valid(self):
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_until

    def __str__(self):
        return f"QR - {self.activity.title}"

class QRScanLog(models.Model):
    qr_session = models.ForeignKey(
        QRAttendanceSession,
        on_delete=models.CASCADE,
        related_name='scans'
    )

    cadet = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'CADET'}
    )

    scanned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevents a cadet from scanning the SAME session twice
        unique_together = ('qr_session', 'cadet')

    def __str__(self):
        return f"{self.cadet.name} scanned {self.qr_session.activity.title}"
# ===============================
# REPORT MODEL
# ===============================

class Report(models.Model):
    REPORT_TYPE_CHOICES = (
        ('ATTENDANCE', 'Attendance Report'),
        ('CAMP', 'Camp Report'),
        ('EVENT', 'Event Report'),
        ('PERFORMANCE', 'Performance Report'),
    )
    
    # NEW: Status tracking for Officer analysis
    STATUS_CHOICES = (
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Needs Revision'),
    )

    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES)
    
    # NEW: Specific Event Metadata (for Place/Date/Time)
    event_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to='reports/')
    
    # NEW: Feedback Loop
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    officer_remarks = models.TextField(null=True, blank=True)
    
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.status}"

# ===============================
# ACHIEVEMENT MODEL
# ===============================

class Achievement(models.Model):

    title = models.CharField(max_length=200)
    description = models.TextField()

    awarded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    awarded_on = models.DateField()

    def __str__(self):
        return self.title

class CadetAchievement(models.Model):

    cadet = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'CADET'}
    )

    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE
    )

    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cadet', 'achievement')

    def __str__(self):
        return f"{self.cadet.name} - {self.achievement.title}"


class Rank(models.Model):

    name = models.CharField(max_length=50)
    level = models.IntegerField()

    def __str__(self):
        return self.name

class RankVacancy(models.Model):
    year = models.IntegerField()
    rank = models.ForeignKey(Rank, on_delete=models.CASCADE)
    vacancy = models.IntegerField()

    class Meta:
        # This prevents the same rank from having two entries in the same year
        unique_together = ('rank', 'year')

    def __str__(self):
        return f"{self.rank.name} - {self.year}"
    
class RankPanel(models.Model):

    cadet = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    rank = models.ForeignKey(
        Rank,
        on_delete=models.CASCADE
    )

    year = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cadet.name} - {self.rank.name}"
    

class NCCHandbook(models.Model):
    CATEGORY_CHOICES = (
        ('COMMON', 'Common Subjects'),
        ('SPECIALIZED', 'Specialized Subjects'),
        ('DRILL', 'Drill Manual'),
        ('WEAPON', 'Weapon Training'),
    )

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    file = models.FileField(upload_to='handbooks/')
    
    # This field stores the extracted text from the PDF for the AI to read
    content_text = models.TextField(blank=True, null=True) 
    
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
@receiver(post_save, sender=NCCHandbook)
def trigger_ai_extraction(sender, instance, created, **kwargs):
    if created:
        # This runs in the background to fill the content_text field
        extract_and_save_pdf_content(instance.id)

from django.db import models
from django.core.exceptions import ValidationError

class UniformItem(models.Model):
    ITEM_TYPE_CHOICES = (
        ('UNIFORM', 'Full Uniform Set'),
        ('BERET', 'Beret'),
        ('BELT', 'Belt'),
        ('TRACK','Track Suit'),
        ('LANYARD', 'Lanyard'),
        ('HACKLE', 'Hackle'),
        ('BOOT','DM Boots'),
        ('NAME PLATE','Name plate'),
        ('SIDE BADGE','Side badge'),
    )

    name = models.CharField(max_length=200)
    item_type = models.CharField(max_length=50, choices=ITEM_TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    image = models.ImageField(upload_to='inventory/', null=True, blank=True)
    total_quantity = models.PositiveIntegerField()
    available_quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.available_quantity > self.total_quantity:
            raise ValidationError("Available quantity cannot be more than total stock.")

    def __str__(self):
        return f"{self.name} (₹{self.price}) - Left: {self.available_quantity}"

class UniformOrder(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Bill Accepted'),
        ('REJECTED', 'Rejected'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('CASH', 'Cash'),
        ('UPI', 'UPI'),
    )

    cadet = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    officer_note = models.TextField(null=True, blank=True) # New field for pickup instructions

    # Method to update total amount automatically
    def update_total(self):
        self.total_amount = sum(item.get_cost() for item in self.items.all())
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(UniformOrder, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(UniformItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2) 

    def get_cost(self):
        return self.price_at_order * self.quantity

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"