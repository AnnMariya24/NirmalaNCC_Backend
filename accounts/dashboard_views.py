from urllib import request

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .permissions import IsProfileCompleted
from .models import Notification, Attendance, CampParticipation  # Ensure these are imported

class CadetDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsProfileCompleted]

    def get(self, request):
        user = request.user
        cadet_profile = user.cadet_profile  # This is the CadetProfile instance
        
        # 1. Notifications (linked to User)
        unread_notifications = Notification.objects.filter(
            user=user, 
            is_read=False
        ).count()

        # 2. Attendance (linked to CadetProfile + String status)
        total_sessions = Attendance.objects.filter(cadet=cadet_profile).count()
        present_sessions = Attendance.objects.filter(
            cadet=cadet_profile, 
            status='PRESENT' # Changed from is_present=True
        ).count()
        
        attendance_val = 0
        if total_sessions > 0:
            attendance_val = round((present_sessions / total_sessions) * 100)

        # 3. Camp Count (linked to User - based on your model)
        # Using 'CampParticipation' based on the model name you provided
        camps_enrolled = CampParticipation.objects.filter(
            cadet=user, 
            status='APPROVED' # Or just count all? Up to you.
        ).count()

        return Response({
            "identity": {
                "name": user.name,
                "email": user.email,
                "cadet_number": cadet_profile.cadet_number,
                "wing": cadet_profile.wing,
                "division": cadet_profile.division,
                "blood_group": cadet_profile.blood_group,
                "profile_photo": cadet_profile.profile_photo.url if cadet_profile.profile_photo else None
            },
            "academic_summary": {
                "course": user.academic_details.course,
                "department": user.academic_details.department,
                "semester": user.academic_details.semester,
                "year_of_joining": user.academic_details.year_of_joining
            },
            "ncc_status": {
                "previously_in_ncc": cadet_profile.previously_in_ncc,
                "previous_ncc_institution": cadet_profile.previous_ncc_institution,
                "previous_ncc_certificate": cadet_profile.previous_ncc_certificate
            },
            "profile_status": {
                "profile_completed": user.profile_completed
            },
            "stats": {
                "notification_count": unread_notifications,
                "attendance_percentage": attendance_val,
                "camp_count": camps_enrolled
            }
        })