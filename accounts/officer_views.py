from time import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q, Count, FloatField
from rest_framework import status

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from accounts import permissions
from accounts.serializers import ReportSerializer, UniformItemSerializer

from .models import Activity, Camp, CampParticipation, Feedback, Notice, Notification, Poll, PollOption, Report, UniformOrder
from .models import Attendance, User, CadetProfile
from .officer_serializers import ActivitySerializer, AttendanceCadetSerializer, CampParticipationSerializer, CampSerializer, FeedbackSerializer, NoticeSerializer, OfficerCadetSerializer, PollSerializer, QRAttendanceSessionSerializer
from django.contrib.auth import get_user_model
from .models import Notification
from .models import Rank, RankVacancy, RankPanel
from .officer_serializers import RankSerializer, RankVacancySerializer, RankPanelSerializer

from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
# from .models import InventoryItem
# from .officer_serializers import InventoryItemSerializer
# # =====================================
# OFFICER DASHBOARD
# =====================================

from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from django.utils import timezone
from datetime import datetime

# Import your other models here
# from .models import Feedback, Report, Notice 

class OfficerDashboardView(APIView):
    def get(self, request):
        # 1. Basic Cadet Stats
        total = User.objects.filter(role="CADET").count()
        approved = User.objects.filter(role="CADET", is_approved=True).count()
        pending = User.objects.filter(role="CADET", is_approved=False).count()
        profile_completed = User.objects.filter(role="CADET", profile_completed=True).count()

        # 2. Feedback & Reports (Assume 'is_viewed' or similar field exists)
        # Change 'Feedback' and 'Report' to your actual model names
        new_feedbacks = Feedback.objects.count() # Or .filter(is_read=False).count()
        total_reports = Report.objects.count()

        # 3. Cadet Strength for 3 Active Years
        current_year = datetime.now().year
        year_stats = {}
        
        # This loops through the current year and the two previous years
        for i in range(3):
            year = current_year - i
            # We filter User, then follow the 'cadet_profile' relationship 
            # to check the 'training_year' field
            count = User.objects.filter(
                role="CADET", 
                cadet_profile__training_year=year
            ).count()
            
            year_stats[f"year_{year}"] = count

        return Response({
            "total_cadets": total,
            "approved_cadets": approved,
            "pending_cadets": pending,
            "profile_completed": profile_completed,
            "new_feedbacks": new_feedbacks,
            "total_reports": total_reports,
            "active_years_breakdown": year_stats,
            "total_3_year_strength": sum(year_stats.values())
        })

# =====================================
# VIEW ALL CADETS
# =====================================

class OfficerCadetsView(APIView):

    def get(self, request):

        year = request.GET.get("training_year")
        division = request.GET.get("division")
        search = request.GET.get("search")

        cadets = CadetProfile.objects.filter(
            user__role="CADET",
            user__is_approved=True
        ).select_related("user")

        if year:
            cadets = cadets.filter(training_year=year)

        if division:
            cadets = cadets.filter(division=division)

        if search:
            cadets = cadets.filter(
                Q(user__name__icontains=search) |
                Q(cadet_number__icontains=search)
            )

        serializer = OfficerCadetSerializer(cadets, many=True)

        return Response({
            "cadets": serializer.data
        })

# =====================================
# PENDING CADETS
# =====================================

class PendingCadetsView(APIView):

    def get(self, request):

        cadets = User.objects.filter(
            role="CADET",
            is_approved=False
        )

        data = []

        for user in cadets:
            data.append({
                "id": user.id,
                "name": user.name,
                "email": user.email
            })

        return Response({
            "cadets": data
        })

# =====================================
# APPROVE CADET
# =====================================

class ApproveCadetView(APIView):

    def post(self, request, pk):

        try:

            user = User.objects.get(id=pk)

            user.is_approved = True
            user.save()

            return Response({
                "message": "Cadet approved successfully"
            })

        except User.DoesNotExist:

            return Response({
                "error": "Cadet not found"
            })


# =====================================
# REJECT CADET
# =====================================

class RejectCadetView(APIView):

    def delete(self, request, pk):

        try:

            user = User.objects.get(id=pk)
            
            user.delete()

            return Response({
                "message": "Cadet rejected and deleted"
            })

        except User.DoesNotExist:

            return Response({
                "error": "Cadet not found"
            })


# =====================================
# SINGLE CADET FULL PROFILE (OFFICER)
# =====================================

class OfficerCadetProfileView(APIView):

    def get(self, request, pk):

        try:

            cadet = CadetProfile.objects.select_related(
                "user",
                "user__personal_details",
                "user__academic_details",
                "user__bank_details",
                "user__identity_details",
                "user__medical_details",
            ).get(id=pk)

            serializer = OfficerCadetSerializer(cadet)

            return Response(serializer.data)

        except CadetProfile.DoesNotExist:

            return Response({
                "error": "Cadet not found"
            }, status=404)


# =====================================
# LOAD CADETS FOR ATTENDANCE
# =====================================

class AttendanceCadetsView(APIView):

    def get(self, request):

        year = request.GET.get("training_year")
        

        cadets = CadetProfile.objects.filter(
            training_year=year,
            
            user__is_approved=True
        ).select_related("user")

        serializer = AttendanceCadetSerializer(cadets, many=True)

        return Response({
            "cadets": serializer.data
        })

from django.db.models.functions import Cast
from django.db.models import Count, Q, FloatField, Case, When, Value

class AttendanceSummaryView(APIView):
    def get(self, request):
        raw_year = request.GET.get("training_year")
        
        try:
            processed_year = int(str(raw_year).split('-')[0])
        except (ValueError, IndexError, TypeError):
            processed_year = 2023

        # Note the change from 'attendance' to 'attendances'
        summary = CadetProfile.objects.filter(
            training_year=processed_year,
            user__is_approved=True
        ).annotate(
            total_sessions=Count('attendances'),
            present_days=Count('attendances', filter=Q(attendances__status='PRESENT')),
        ).annotate(
            percentage=Case(
                When(total_sessions=0, then=Value(0.0)),
                default=Cast(Count('attendances', filter=Q(attendances__status='PRESENT')), FloatField()) 
                        / Cast(Count('attendances'), FloatField()) * 100.0,
                output_field=FloatField()
            )
        ).values('id', 'user__name', 'cadet_number', 'present_days', 'total_sessions', 'percentage')

        formatted_summary = [
            {
                "id": item['id'],
                "name": item['user__name'],
                "cadet_number": item['cadet_number'],
                "present_days": item['present_days'],
                "total_sessions": item['total_sessions'],
                "percentage": round(item['percentage'] or 0.0, 2)
            } for item in summary
        ]

        return Response({"summary": formatted_summary})
    
# =====================================
# MARK ATTENDANCE (Existing - Remains Same)
# =====================================
class MarkAttendanceView(APIView):
    def post(self, request):
        activity_id = request.data.get("activity")
        records = request.data.get("records", [])

        # 1. Get the activity
        activity = get_object_or_404(Activity, id=activity_id)

        try:
            for record in records:
                # 2. Use 'get_or_create' instead of 'update_or_create'
                # This only saves if a record doesn't already exist for this cadet/activity
                obj, created = Attendance.objects.get_or_create(
                    cadet_id=record["cadet_id"],
                    activity=activity,
                    defaults={
                        "status": record["status"],
                        "marked_by": request.user
                    }
                )
                # If created is False, it means the record was already there
                if not created:
                    print(f"Skipping cadet {record['cadet_id']} - Attendance already exists.")

            return Response({"message": "Processed successfully. New records created where missing."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
# ===============================
# CREATE ACTIVITY
# ===============================

class CreateActivityView(APIView):

    def post(self, request):

        serializer = ActivitySerializer(data=request.data)

        if serializer.is_valid():

            serializer.save(created_by=request.user)

            return Response(
                {
                    "message": "Activity created successfully",
                    "activity": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ===============================
# LIST ACTIVITIES
# ===============================

class ActivityListView(APIView):

    def get(self, request):

        activities = Activity.objects.all().order_by("-date")

        serializer = ActivitySerializer(activities, many=True)

        return Response({
            "activities": serializer.data
        })


# ===============================
# ACTIVITY DETAIL
# ===============================

class ActivityDetailView(APIView):

    def get(self, request, activity_id):

        try:
            activity = Activity.objects.get(id=activity_id)
        except Activity.DoesNotExist:
            return Response(
                {"error": "Activity not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ActivitySerializer(activity)

        return Response(serializer.data)


# ===============================
# UPDATE ACTIVITY
# ===============================

class UpdateActivityView(APIView):

    def put(self, request, activity_id):

        try:
            activity = Activity.objects.get(id=activity_id)
        except Activity.DoesNotExist:
            return Response(
                {"error": "Activity not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ActivitySerializer(
            activity,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response({
                "message": "Activity updated successfully",
                "activity": serializer.data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ===============================
# DELETE ACTIVITY
# ===============================

class DeleteActivityView(APIView):

    def delete(self, request, activity_id):

        try:
            activity = Activity.objects.get(id=activity_id)
        except Activity.DoesNotExist:
            return Response(
                {"error": "Activity not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        activity.delete()

        return Response({
            "message": "Activity deleted successfully"
        })

class CreateCampView(APIView):

    def post(self, request):

        serializer = CampSerializer(data=request.data)

        if serializer.is_valid():

            serializer.save(created_by=request.user)

            return Response({
                "message": "Camp created successfully",
                "camp": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CampListView(APIView):

    def get(self, request):

        camps = Camp.objects.all().order_by("-start_date")

        serializer = CampSerializer(camps, many=True)

        return Response({
            "camps": serializer.data
        })

class UpdateCampView(APIView):

    def put(self, request, camp_id):

        try:
            camp = Camp.objects.get(id=camp_id)
        except Camp.DoesNotExist:
            return Response({"error": "Camp not found"}, status=404)

        serializer = CampSerializer(
            camp,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response({
                "message": "Camp updated",
                "camp": serializer.data
            })

        return Response(serializer.errors, status=400)
    
class DeleteCampView(APIView):

    def delete(self, request, camp_id):

        try:
            camp = Camp.objects.get(id=camp_id)
        except Camp.DoesNotExist:
            return Response({"error": "Camp not found"}, status=404)

        camp.delete()

        return Response({
            "message": "Camp deleted"
        })
    

class UpdateCampParticipationStatus(APIView):

    def put(self, request, participation_id):

        try:
            participation = CampParticipation.objects.get(
                id=participation_id
            )
        except CampParticipation.DoesNotExist:
            return Response({"error": "Record not found"}, status=404)

        new_status = request.data.get("status")

        if new_status not in ["APPROVED", "REJECTED", "COMPLETED"]:
            return Response({"error": "Invalid status"})

        camp = participation.camp

        if new_status == "APPROVED":

            approved_count = camp.participants.filter(
                status="APPROVED"
            ).count()

            if approved_count >= camp.total_seats:
                return Response({
                    "error": "No seats left"
                })

        participation.status = new_status
        participation.save()

        return Response({
            "message": "Status updated"
        })

class CampParticipantsView(APIView):

    def get(self, request, camp_id):

        participants = CampParticipation.objects.filter(
            camp_id=camp_id
        )

        serializer = CampParticipationSerializer(
            participants,
            many=True
        )

        return Response({
            "participants": serializer.data
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_notice(request):

    serializer = NoticeSerializer(data=request.data)

    if serializer.is_valid():

        notice = serializer.save(created_by=request.user)

        # 🔔 CREATE NOTIFICATIONS FOR ALL CADETS
        send_notice_notification(
                title="New Notice Posted",
                message=notice.title
            )

        # Determine target users
        if notice.target_role == "ALL":
            users = User.objects.all()

        elif notice.target_role == "CADET":
            users = User.objects.filter(role="CADET")

        elif notice.target_role == "OFFICER":
            users = User.objects.filter(role="OFFICER")

        else:
            users = []

        notifications = []

        for user in users:
            notifications.append(
                Notification(
                    user=user,
                    title=notice.title,
                    message=notice.message,
                    notification_type="NOTICE"
                )
            )

        Notification.objects.bulk_create(notifications)

        return Response(
            {"message": "Notice created successfully"},
            status=201
        )

    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_notices(request):

    user = request.user

    notices = Notice.objects.filter(is_active=True)

    if user.role == "CADET":
        notices = notices.filter(
            target_role__in=["ALL", "CADET"]
        )

    elif user.role == "OFFICER":
        notices = notices.filter(
            target_role__in=["ALL", "OFFICER"]
        )

    serializer = NoticeSerializer(notices, many=True)

    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notice(request, id):

    try:
        notice = Notice.objects.get(id=id)
    except Notice.DoesNotExist:
        return Response({"error": "Notice not found"}, status=404)

    if notice.created_by != request.user:
        return Response({"error": "Not allowed"}, status=403)

    notice.delete()

    return Response({"message": "Notice deleted successfully"}, status=200)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_notice(request, id):

    try:
        notice = Notice.objects.get(id=id)
    except Notice.DoesNotExist:
        return Response({"error": "Notice not found"}, status=404)

    if notice.created_by != request.user:
        return Response({"error": "Not allowed"}, status=403)

    serializer = NoticeSerializer(notice, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Notice updated successfully"})

    return Response(serializer.errors, status=400)

class OfficerFeedbackListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        feedbacks = Feedback.objects.filter(
    cadet__role="CADET"
).order_by("-created_at")
        serializer = FeedbackSerializer(feedbacks, many=True)
        return Response(serializer.data)

class CreatePollView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        question = request.data.get("question")
        options = request.data.get("options")

        poll = Poll.objects.create(
            question=question,
            created_by=request.user
        )

        for opt in options:
            PollOption.objects.create(
                poll=poll,
                option_text=opt
            )

        return Response({"message": "Poll created successfully"})

class RespondFeedbackView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        feedback_id = request.data.get("feedback_id")
        response_text = request.data.get("response")
        status = request.data.get("status")

        feedback = Feedback.objects.get(id=feedback_id)

        feedback.response = response_text
        feedback.status = status
        feedback.responded_by = request.user
        feedback.responded_at = timezone.now()

        feedback.save()

        return Response({"message": "Feedback responded successfully"})

class PollResultView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, poll_id):

        poll = Poll.objects.get(id=poll_id)

        options = PollOption.objects.filter(
            poll=poll
        ).annotate(
            votes=Count('pollvote')
        )

        total_votes = sum(option.votes for option in options)

        results = []

        for option in options:

            percentage = 0
            if total_votes > 0:
                percentage = round((option.votes / total_votes) * 100, 2)

            results.append({
                "option": option.option_text,
                "votes": option.votes,
                "percentage": percentage
            })

        return Response({
            "question": poll.question,
            "total_votes": total_votes,
            "results": results
        })

class PollDetailView(APIView):
    permission_classes = [IsAuthenticated]

    # PATCH /api/polls/<id>/
    def patch(self, request, pk):
        poll = get_object_or_404(Poll, pk=pk)
        serializer = PollSerializer(poll, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE /api/polls/<id>/
    def delete(self, request, pk):
        poll = get_object_or_404(Poll, pk=pk)
        poll.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

User = get_user_model()

def send_notice_notification(title, message):

    cadets = User.objects.filter(role='CADET', is_approved=True)

    notifications = [
        Notification(
            user=cadet,
            title=title,
            message=message,
            notification_type='NOTICE'
        )
        for cadet in cadets
    ]

    Notification.objects.bulk_create(notifications)

import uuid

def send_notice_notification(title, message):
    cadets = User.objects.filter(role='CADET', is_approved=True)
    batch_id = str(uuid.uuid4()) # Create a unique ID for this specific announcement

    notifications = [
        Notification(
            user=cadet,
            title=title,
            message=message,
            notification_type='NOTICE',
            group_id=batch_id # Attach the ID to every record in this batch
        )
        for cadet in cadets
    ]

    Notification.objects.bulk_create(notifications)



class ManageNotificationView(APIView):
    permission_classes = [IsAuthenticated] # Should be restricted to Officers

    def delete(self, request, group_id):
        # This deletes the notice for EVERY cadet at once
        Notification.objects.filter(group_id=group_id).delete()
        return Response({"message": "Notice retracted successfully"})

    def put(self, request, group_id):
        # This updates the notice for EVERY cadet at once
        new_title = request.data.get('title')
        new_msg = request.data.get('message')
        
        Notification.objects.filter(group_id=group_id).update(
            title=new_title, 
            message=new_msg
        )
        return Response({"message": "Notice updated successfully"})
    

class RankListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        ranks = Rank.objects.all().order_by("-level")

        serializer = RankSerializer(ranks, many=True)

        return Response(serializer.data)
    


class SetRankVacancyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1. Extract the unique identifiers from the request
        rank_id = request.data.get("rank")
        year = request.data.get("year")
        vacancy_count = request.data.get("vacancy")

        if not rank_id or not year or vacancy_count is None:
            return Response(
                {"error": "Rank, Year, and Vacancy are required fields."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. update_or_create: 
        # It looks for a record matching 'rank_id' and 'year'.
        # If found, it updates 'vacancy'. If not, it creates a new entry.
        vacancy_obj, created = RankVacancy.objects.update_or_create(
            rank_id=rank_id, 
            year=year,
            defaults={'vacancy': vacancy_count}
        )

        # 3. Return the data using your existing serializer
        serializer = RankVacancySerializer(vacancy_obj)
        
        # We return a 200 OK for updates and 201 Created for new ones
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

class CreateRankPanelView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = RankPanelSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors)

class RankPanelListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        year = request.query_params.get("year")

        panel = RankPanel.objects.filter(year=year)

        serializer = RankPanelSerializer(panel, many=True)

        return Response(serializer.data)

class CadetListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        cadets = User.objects.filter(role="CADET")
        data = [
            {"id": c.id, "name": c.name}
            for c in cadets
        ]
        return Response(data)
    
from django.shortcuts import get_object_or_404

# 1. New View to list vacancies (This fixes the "SUO 1" format)
class RankVacancyListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = request.query_params.get("year")
        vacancies = RankVacancy.objects.filter(year=year)
        # We need a serializer that includes the rank_name
        data = []
        for v in vacancies:
            data.append({
                "id": v.id,
                "rank": v.rank.id,
                "rank_name": v.rank.name,
                "year": v.year,
                "vacancy": v.vacancy # This maps to the 'vacancy' field in your model
            })
        return Response(data)

# 2. New View to Delete/Update
class RankVacancyDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        vacancy_obj = get_object_or_404(RankVacancy, pk=pk)
        vacancy_obj.vacancy = request.data.get("vacancy", vacancy_obj.vacancy)
        vacancy_obj.save()
        return Response({"status": "updated"})

    def delete(self, request, pk):
        vacancy_obj = get_object_or_404(RankVacancy, pk=pk)
        vacancy_obj.delete()
        return Response(status=204)

from django.db.models import Count

class RankAvailabilityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = request.query_params.get("year")
        
        # Get all vacancies for the year
        vacancies = RankVacancy.objects.filter(year=year)
        
        # Get current assignments count for the year
        assignments = RankPanel.objects.filter(year=year).values('rank').annotate(total=Count('id'))
        assignment_map = {item['rank']: item['total'] for item in assignments}

        data = []
        for v in vacancies:
            data.append({
                "rank_id": v.rank.id,
                "rank_name": v.rank.name,
                "total_slots": v.vacancy,
                "filled_slots": assignment_map.get(v.rank.id, 0),
                "remaining": v.vacancy - assignment_map.get(v.rank.id, 0)
            })
        return Response(data)

class ResetRankPanelView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        year = request.query_params.get('year')
        if not year:
            return Response({"error": "Year is required"}, status=400)
            
        # Delete all assignments for the specific year
        deleted_count, _ = RankPanel.objects.filter(year=year).delete()
        
        return Response({
            "message": f"Successfully deleted {deleted_count} assignments for {year}."
        })
    
# class InventoryViewSet(viewsets.ModelViewSet):
#     queryset = InventoryItem.objects.all().order_by('name')
#     serializer_class = InventoryItemSerializer
#     # This parser_classes allows uploading images via form-data
#     parser_classes = (MultiPartParser, FormParser, JSONParser)

# class OrderViewSet(viewsets.ModelViewSet):
#     serializer_class = UniformOrderSerializer

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_staff or (hasattr(user, 'role') and user.role == 'OFFICER'):
#             return UniformOrder.objects.all().order_by('-created_at')
#         return UniformOrder.objects.filter(cadet=user).order_by('-created_at')

#     @action(detail=False, methods=['post'], url_path='create-bill')
#     def create_bill(self, request):
#         """
#         Receives a list of items (cart) and creates one Bill.
#         Expected Data: { "items": [{"id":1, "qty":2}], "payment_method": "UPI" }
#         """
#         data = request.data
#         items_data = data.get('items', [])
        
#         if not items_data:
#             return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

#         # 1. Create the Main Order (The Bill)
#         order = UniformOrder.objects.create(
#             cadet=request.user,
#             payment_method=data.get('payment_method'),
#             status='PENDING'
#         )

#         running_total = 0
#         for entry in items_data:
#             inventory_item = InventoryItem.objects.get(id=entry['id'])
#             qty = int(entry['qty'])
            
#             # 2. Create individual items linked to bill
#             OrderItem.objects.create(
#                 order=order,
#                 item=inventory_item,
#                 quantity=qty,
#                 price_at_order=inventory_item.price
#             )
#             running_total += (inventory_item.price * qty)

#         order.total_amount = running_total
#         order.save()

#         return Response({"message": "Bill generated successfully", "bill_id": order.id})

#     @action(detail=True, methods=['post'], url_path='approve')
#     def approve_order(self, request, pk=None):
#         """Officer approves the bill and stock is deducted"""
#         order = self.get_object()
        
#         # Check stock for all items first
#         for oi in order.items.all():
#             if oi.item.available_quantity < oi.quantity:
#                 return Response({"error": f"Insufficient stock for {oi.item.name}"}, status=400)

#         # Deduct Stock
#         for oi in order.items.all():
#             inv = oi.item
#             inv.available_quantity -= oi.quantity
#             inv.save()

#         order.status = 'APPROVED'
#         order.save()
#         return Response({"message": "Bill approved and items issued."})
    

class OfficerReportActionView(APIView):

    def patch(self, request, pk):
        try:
            report = Report.objects.get(pk=pk)
            # Officer can only update status and remarks
            report.status = request.data.get('status', report.status)
            report.officer_remarks = request.data.get('officer_remarks', report.officer_remarks)
            report.save()
            return Response({"message": "Report reviewed successfully"})
        except Report.DoesNotExist:
            return Response({"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND)
        
class OfficerReportListView(APIView):
    def get(self, request):
        reports = Report.objects.all().order_by('-generated_at')
        # Pass context={'request': request} so the serializer can see the user/URL
        serializer = ReportSerializer(reports, many=True, context={'request': request})
        return Response(serializer.data)
    
# 1. OFFICER VIEW: Generate/Create QR Session
class CreateQRSessionView(APIView):
    

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=401)

        if request.user.role != 'OFFICER':
            return Response({"error": "Unauthorized"}, status=403)
            
        serializer = QRAttendanceSessionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import UniformOrder, UniformItem
from .officer_serializers import UniformItemSerializer, UniformOrderSerializer

from rest_framework.generics import get_object_or_404

class OfficerInventoryView(APIView):
    # 1. READ: View all items in the inventory
    def get(self, request):
        items = UniformItem.objects.all().order_by('-created_at')
        serializer = UniformItemSerializer(items, many=True)
        return Response(serializer.data)

    # 2. CREATE: Add a new item (Nomenclature)
    def post(self, request):
        serializer = UniformItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 3. UPDATE: Change details of an existing item
    def patch(self, request, pk=None):
        # pk is the ID of the item to update
        item = get_object_or_404(UniformItem, pk=pk)
        serializer = UniformItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 4. DELETE: Remove an item from the system
    def delete(self, request, pk=None):
        item = get_object_or_404(UniformItem, pk=pk)
        item.delete()
        return Response({"message": "Item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
class OfficerOrderReviewView(APIView):
    """Officer can list, approve, or reject order requests"""

    # --- NEW: List all pending orders for the officer ---
    def get(self, request):
        # We order by created_at so newest requests appear at the top
        orders = UniformOrder.objects.filter(status='PENDING').order_by('-created_at')
        serializer = UniformOrderSerializer(orders, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def patch(self, request, order_id):
        try:
            order = UniformOrder.objects.select_for_update().get(id=order_id)
            new_status = request.data.get('status')
            # Capture the pickup/rejection message from the frontend
            officer_message = request.data.get('officer_note') 

            if order.status != 'PENDING':
                return Response({"error": "Order already processed"}, status=status.HTTP_400_BAD_REQUEST)

            if new_status == 'APPROVED':
                for order_item in order.items.all():
                    inventory_item = order_item.item
                    if inventory_item.available_quantity < order_item.quantity:
                        return Response({
                            "error": f"Insufficient stock for {inventory_item.name}"
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    inventory_item.available_quantity -= order_item.quantity
                    inventory_item.save()
                
                order.status = 'APPROVED'
            
            elif new_status == 'REJECTED':
                order.status = 'REJECTED'
            
            else:
                return Response({"error": "Invalid status provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Save the message so the Cadet can see it
            order.officer_note = officer_message 
            order.save()
            
            return Response({
                "message": f"Order marked as {new_status}", 
                "status": order.status,
                "officer_note": order.officer_note
            })

        except UniformOrder.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND) 