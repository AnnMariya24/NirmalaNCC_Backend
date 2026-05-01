from rest_framework import generics,permissions

from accounts.ai_service import NCCAIHandler
from accounts.officer_serializers import FeedbackSerializer, NotificationSerializer, PollSerializer
from .models import CampParticipation,  NCCHandbook, Poll, PollOption, PollVote, QRAttendanceSession, QRScanLog, Report, UniformItem, User
from .serializers import AttendanceSerializer, CadetCampSerializer, CadetFeedbackSerializer, NCCHandbookSerializer, RegisterSerializer, ReportSerializer, UniformItemSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .serializers import LoginSerializer
from rest_framework.parsers import MultiPartParser, FormParser


from rest_framework.decorators import api_view, permission_classes

from .models import (
    CadetProfile,
    PersonalDetails,
    AcademicDetails,
    BankDetails,
    IdentityDetails,
    MedicalDetails,
    Document
)
from .serializers import (
    CadetProfileSerializer,
    PersonalDetailsSerializer,
    AcademicDetailsSerializer,
    BankDetailsSerializer,
    IdentityDetailsSerializer,
    MedicalDetailsSerializer,
    DocumentSerializer
)
from django.db.models import Count
from datetime import date, timedelta
from .models import (
    Attendance,
    Camp,
    Notice,
    Achievement,
    Notification,
   
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# ==========================
# CADET CORE
# ==========================

class CadetProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CadetProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = CadetProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile


# ==========================
# PERSONAL DETAILS
# ==========================

class PersonalDetailsView(generics.RetrieveUpdateAPIView):
    serializer_class = PersonalDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return PersonalDetails.objects.filter(
            user=self.request.user
        ).first()

    def update(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj is None:
            # 🔥 DO NOT pass user here
            serializer = self.get_serializer(
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()   # ← IMPORTANT (no user=)
            return Response(serializer.data)

        serializer = self.get_serializer(
            obj,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ==========================
# ACADEMIC DETAILS
# ==========================

class AcademicDetailsView(generics.RetrieveUpdateAPIView):
    serializer_class = AcademicDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return AcademicDetails.objects.filter(
            user=self.request.user
        ).first()

    def update(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj is None:
            serializer = self.get_serializer(
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        serializer = self.get_serializer(
            obj,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ==========================
# BANK DETAILS
# ==========================

class BankDetailsView(generics.RetrieveUpdateAPIView):
    serializer_class = BankDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return BankDetails.objects.filter(
            user=self.request.user
        ).first()

    def update(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj is None:
            serializer = self.get_serializer(
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        serializer = self.get_serializer(
            obj,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ==========================
# IDENTITY DETAILS
# ==========================

class IdentityDetailsView(generics.RetrieveUpdateAPIView):
    serializer_class = IdentityDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return IdentityDetails.objects.filter(
            user=self.request.user
        ).first()

    def update(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj is None:
            serializer = self.get_serializer(
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        serializer = self.get_serializer(
            obj,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ==========================
# MEDICAL DETAILS
# ==========================

class MedicalDetailsView(generics.RetrieveUpdateAPIView):
    serializer_class = MedicalDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return MedicalDetails.objects.filter(
            user=self.request.user
        ).first()

    def update(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj is None:
            serializer = self.get_serializer(
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        serializer = self.get_serializer(
            obj,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ==========================
# DOCUMENT UPLOAD
# ==========================

class DocumentUploadView(generics.CreateAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ProfileStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        data = {
            "profile_completed": user.profile_completed,
            "cadet_profile": hasattr(user, "cadet_profile"),
            "personal_details": hasattr(user, "personal_details"),
            "academic_details": hasattr(user, "academic_details"),
            "bank_details": hasattr(user, "bank_details"),
            "identity_details": hasattr(user, "identity_details"),
            "medical_details": hasattr(user, "medical_details"),
        }

        return Response(data)


# ==========================
# COMPLETE PROFILE
# ==========================

class CompleteProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        # Check if all required sections exist
        required_sections = [
            hasattr(user, "cadet_profile"),
            hasattr(user, "personal_details"),
            hasattr(user, "academic_details"),
            hasattr(user, "bank_details"),
            hasattr(user, "identity_details"),
            hasattr(user, "medical_details"),
        ]

        if not all(required_sections):
            return Response(
                {"error": "Complete all sections before finishing."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.profile_completed = True
        user.save()

        # Start 10-day edit window NOW
        profile = user.cadet_profile
        profile.profile_editable_until = (
            timezone.now() + timedelta(days=10)
        )
        profile.edit_permission_granted = False
        profile.save()

        return Response(
            {"message": "Profile completed successfully."},
            status=status.HTTP_200_OK
        )
    

# ===============================
# MAIN DASHBOARD API
# ===============================

class CadetDashboardView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        user = request.user

        attendance = Attendance.objects.filter(user=user)
        total = attendance.count()
        present = attendance.filter(status="PRESENT").count()

        attendance_percentage = (
            (present / total) * 100 if total > 0 else 0
        )

        upcoming_camps = Camp.objects.filter(
            is_active=True,
            start_date__gte=date.today()
        )[:3]

        notices = Notice.objects.all()[:5]

        achievements = Achievement.objects.filter(user=user)[:5]

        unread_notifications = Notification.objects.filter(
            user=user,
            is_read=False
        ).count()

        return Response({
            "cadet_name": user.get_full_name(),
            "email": user.email,
            "attendance_percentage": round(attendance_percentage, 2),
            "total_attendance": total,
            "present_count": present,
            #"upcoming_camps": CampSerializer(upcoming_camps, many=True).data,
            #"notices": NoticeSerializer(notices, many=True).data,
            #"achievements": AchievementSerializer(achievements, many=True).data,
            #"unread_notifications": unread_notifications,
        })



# ==========================
# REQUEST CORRECTION
# ==========================
class RequestCorrectionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        profile = CadetProfile.objects.get(
            user=request.user
        )

        if profile.can_edit():
            return Response(
                {"message": "Profile is already editable."},
                status=400
            )

        profile.correction_requested = True
        profile.save()

        return Response(
            {"message": "Correction request sent to officer."}
        )
    

# ==========================================
# FULL CADET PROFILE VIEW
# ==========================================

class FullCadetProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        data = {}

        # =====================
        # Basic Identity
        # =====================
        data["identity"] = {
            "name": user.name,
            "email": user.email,
            "profile_completed": user.profile_completed,
        }

        # =====================
        # Cadet Core Profile
        # =====================
        try:
            cadet_profile = user.cadet_profile
            data["cadet_profile"] = CadetProfileSerializer(
                cadet_profile
            ).data

            # Edit Status Logic
            now = timezone.now()
            can_edit = False

            if cadet_profile.profile_editable_until:
                if now <= cadet_profile.profile_editable_until:
                    can_edit = True

            if cadet_profile.edit_permission_granted:
                can_edit = True

            data["edit_status"] = {
                "can_edit": can_edit,
                "editable_until": cadet_profile.profile_editable_until,
            }

        except CadetProfile.DoesNotExist:
            data["cadet_profile"] = None
            data["edit_status"] = {
                "can_edit": False,
                "editable_until": None,
            }

        # =====================
        # Other Sections
        # =====================

        data["personal_details"] = (
            PersonalDetailsSerializer(user.personal_details).data
            if hasattr(user, "personal_details")
            else None
        )

        data["academic_details"] = (
            AcademicDetailsSerializer(user.academic_details).data
            if hasattr(user, "academic_details")
            else None
        )

        data["bank_details"] = (
            BankDetailsSerializer(user.bank_details).data
            if hasattr(user, "bank_details")
            else None
        )

        data["identity_details"] = (
            IdentityDetailsSerializer(user.identity_details).data
            if hasattr(user, "identity_details")
            else None
        )

        data["medical_details"] = (
            MedicalDetailsSerializer(user.medical_details).data
            if hasattr(user, "medical_details")
            else None
        )

        return Response(data)

class PersonalDetailsUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request):

        try:
            personal = request.user.personal_details
        except PersonalDetails.DoesNotExist:
            return Response(
                {"error": "Personal details not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PersonalDetailsSerializer(
            personal,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

class CadetProfileUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request):

        cadet = request.user.cadet_profile

        serializer = CadetProfileSerializer(
            cadet,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

class AcademicDetailsUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request):

        academic = request.user.academic_details

        serializer = AcademicDetailsSerializer(
            academic,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

class BankDetailsUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request):

        bank = request.user.bank_details

        serializer = BankDetailsSerializer(
            bank,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

class IdentityDetailsUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request):

        identity = request.user.identity_details

        serializer = IdentityDetailsSerializer(
            identity,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

class MedicalDetailsUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request):

        medical = request.user.medical_details

        serializer = MedicalDetailsSerializer(
            medical,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

class ProfilePhotoUploadView(APIView):

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):

        cadet = request.user.cadet_profile

        photo = request.FILES.get("profile_photo")

        if not photo:
            return Response(
                {"error": "No image uploaded"},
                status=400
            )

        cadet.profile_photo = photo
        cadet.save()

        return Response({
            "profile_photo": cadet.profile_photo.url
        })
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_notifications(request):
    # AUTO-HIDE: Filter for only last 30 days
    one_month_ago = timezone.now() - timedelta(days=30)
    
    notifications = Notification.objects.filter(
        user=request.user,
        created_at__gte=one_month_ago # Only show fresh alerts
    ).order_by("-created_at")

    data = []
    for n in notifications:
        data.append({
            "id": n.id,
            "group_id": n.group_id, # REQUIRED for the Flutter Settings icon
            "title": n.title,
            "message": n.message,
            "type": n.notification_type,
            "is_read": n.is_read,
            "created_at": n.created_at,
        })

    return Response(data)

class SubmitFeedbackView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = CadetFeedbackSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(cadet=request.user)
            return Response({"message": "Feedback submitted successfully"})

        return Response(serializer.errors)
    
class ActivePollListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        polls = Poll.objects.filter(is_active=True)

        serializer = PollSerializer(polls, many=True)

        return Response(serializer.data)
    
class VotePollView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        poll_id = request.data.get("poll_id")
        option_id = request.data.get("option_id")

        poll = Poll.objects.get(id=poll_id)

        # check if cadet already voted
        if PollVote.objects.filter(
            poll=poll,
            cadet=request.user
        ).exists():
            return Response(
                {"message": "You have already voted in this poll"},
                status=400
            )

        option = PollOption.objects.get(id=option_id)

        PollVote.objects.create(
            poll=poll,
            option=option,
            cadet=request.user
        )

        return Response({"message": "Vote recorded successfully"})

class UserNotificationListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        notifications = Notification.objects.filter(
            user=request.user
        ).order_by("-created_at")

        serializer = NotificationSerializer(notifications, many=True)

        return Response(serializer.data)

class MarkNotificationReadView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, notification_id):

        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=request.user
            )
        except Notification.DoesNotExist:
            return Response(
                {"error": "Notification not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        notification.is_read = True
        notification.save()

        return Response({"message": "Notification marked as read"})

class UnreadNotificationCountView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        return Response({"unread_count": count})
    
# class InventoryListView(generics.ListAPIView):
#     queryset = InventoryItem.objects.filter(available_quantity__gt=0)
#     serializer_class = InventoryItemSerializer
#     permission_classes = [IsAuthenticated]

# class UniformRequestCreateView(generics.CreateAPIView):
#     serializer_class = UniformRequestSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         # Automatically assign the logged-in cadet to the request
#         serializer.save(cadet=self.request.user)

# class CadetRequestListView(generics.ListAPIView):
#     """View for the Cadet to see their own requests/bills"""
#     serializer_class = UniformRequestSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return UniformOrder.objects.filter(cadet=self.request.user).order_by('-requested_at')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cadet_camp_list(request):
    """List all future camps for the cadet."""
    from django.utils import timezone
    camps = Camp.objects.filter(end_date__gte=timezone.now().date()).order_by('start_date')
    
    # Passing request to context so the serializer can check 'is_applied'
    serializer = CadetCampSerializer(camps, many=True, context={'request': request})
    return Response({"camps": serializer.data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cadet_show_interest(request):
    """Create a participation record for a camp."""
    camp_id = request.data.get('camp_id')
    
    try:
        camp = Camp.objects.get(id=camp_id)
        
        # Check if seats are actually available
        if camp.seats_left() <= 0:
            return Response({"error": "Camp is full"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the participation (unique_together handles duplicates)
        participation, created = CampParticipation.objects.get_or_create(
            cadet=request.user,
            camp=camp,
            defaults={'status': 'APPLIED'}
        )

        if not created:
            return Response({"message": "Already applied"}, status=status.HTTP_200_OK)
            
        return Response({"message": "Interest registered!"}, status=status.HTTP_201_CREATED)

    except Camp.DoesNotExist:
        return Response({"error": "Camp not found"}, status=status.HTTP_404_NOT_FOUND)
    

from django.shortcuts import get_object_or_404

class CadetAttendanceDetailView(APIView):
    # Ensure only logged-in users can access this
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 1. Safely get the Cadet profile associated with the logged-in user
        # This will return a 404 error if the user is an Admin/Officer 
        # but doesn't have a Cadet profile record.
        cadet = get_object_or_404(CadetProfile, user=request.user)

        # 2. Fetch records efficiently
        records = Attendance.objects.filter(
            cadet=cadet
        ).select_related('activity').order_by('-activity__date')

        # 3. Use list comprehension to format history
        attendance_data = [
            {
                # Safely fallback if 'name' doesn't exist on activity
                "activity_name": getattr(r.activity, "name", getattr(r.activity, "title", "Unknown")),
                "date": r.activity.date.strftime("%Y-%m-%d"),
                "status": r.status.upper(),
            }
            for r in records
        ]

        # 4. Calculate stats
        total = records.count()
        # Case-insensitive check for 'present'
        present = records.filter(status__iexact='PRESENT').count()
        absent = total - present
        
        percentage = (present / total * 100) if total > 0 else 0

        return Response({
            "cadet_name": request.user.name,
            "percentage": round(percentage, 1),
            "total_sessions": total,
            "present": present,
            "absent": absent,
            "history": attendance_data
        }, status=status.HTTP_200_OK)
    
class CadetReportListView(APIView):
    """
    Cadets can view their own reports and upload new ones.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        # Only show reports submitted by the logged-in cadet
        reports = Report.objects.filter(generated_by=request.user).order_by('-generated_at')
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ReportSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

from rest_framework.views import APIView
from rest_framework.response import Response
from .ai_service import NCCAIHandler  # Import your new service class

class NCCChatBotView(APIView):
    def post(self, request):
        user_query = request.data.get('query')
        
        if not user_query:
            return Response({"error": "No query provided"}, status=400)

        # Simply call the static method from your service file
        ai_response = NCCAIHandler.ask_ai(user_query)

        return Response({
            "response": ai_response
        })

class StudyMaterialListCreateView(generics.ListCreateAPIView):
    """
    Handles GET (Listing all materials) 
    and POST (Officer uploading a new PDF)
    """
    queryset = NCCHandbook.objects.all().order_by('-uploaded_at')
    serializer_class = NCCHandbookSerializer
    
    # Allow any authenticated user to view/upload for your BCA project
    # You can later restrict POST to Officers only if needed
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # This saves the record. 
        # The 'post_save' signal in models.py will then trigger the AI extraction.
        serializer.save()


# 2. CADET VIEW: Scan QR and Mark Attendance
class ScanQRAttendanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        qr_code_token = request.data.get('qr_code')
        
        # 1. Validate Session
        session = get_object_or_404(QRAttendanceSession, qr_code=qr_code_token, is_active=True)
        
        if not session.is_currently_valid:
            return Response({"error": "This QR code has expired."}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Get Cadet Profile
        try:
            cadet_profile = CadetProfile.objects.get(user=request.user)
        except CadetProfile.DoesNotExist:
            return Response({"error": "Cadet profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # 3. Log the Scan and Update Main Attendance Table
        try:
            # Create the Scan Log
            QRScanLog.objects.create(qr_session=session, cadet=request.user)
            
            # Update/Create the actual Attendance record
            Attendance.objects.update_or_create(
                cadet=cadet_profile,
                activity=session.activity,
                defaults={
                    'status': 'PRESENT',
                    'is_approved': True  # Optional: Auto-approve since QR is secure
                }
            )
            
            return Response({
                "message": f"Attendance marked for {session.activity.title}!",
                "status": "PRESENT"
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            # This catches the 'unique_together' error if they scan twice
            return Response({"error": "Attendance already marked for this session."}, status=status.HTTP_400_BAD_REQUEST)
    
from django.db import transaction
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import UniformOrder, UniformItem
from .serializers import CadetOrderSerializer, UniformItemSerializer

class CadetInventoryListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Return only items currently in stock for the cadet gallery
        items = UniformItem.objects.filter(available_quantity__gt=0)
        serializer = UniformItemSerializer(items, many=True)
        return Response(serializer.data)

class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Pass the request in context so the serializer can access request.user
        serializer = CadetOrderSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            try:
                # .save() calls the .create() method inside your CadetOrderSerializer
                order = serializer.save()
                return Response({
                    "message": "Requisition submitted to Officer successfully!", 
                    "order_id": order.id,
                    "total": order.total_amount,
                    "status": order.status
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyBillsListView(generics.ListAPIView):
    """
    Cadet view to see their own Virtual Bills / Order History.
    """
    # Use the CadetOrderSerializer (or a dedicated DetailSerializer) 
    # to show the items within the bill
    serializer_class = CadetOrderSerializer 
    permission_classes = [IsAuthenticated]
    

    def get_queryset(self):
        return UniformOrder.objects.filter(
            cadet=self.request.user
        ).prefetch_related('items__item').order_by('-created_at')