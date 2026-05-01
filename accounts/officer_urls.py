
from django.urls import path,include
from .officer_views import *
from accounts import officer_views





urlpatterns = [

    path("dashboard/", OfficerDashboardView.as_view()),

    path("cadets/", OfficerCadetsView.as_view()),

    path("cadets/pending/", PendingCadetsView.as_view()),

    path("cadets/<int:pk>/approve/", ApproveCadetView.as_view()),

    path("cadets/<int:pk>/reject/", RejectCadetView.as_view()),
    path(
    "cadet/<int:pk>/",
    OfficerCadetProfileView.as_view(),
),
path(
        "attendance/cadets/",
        AttendanceCadetsView.as_view()
    ),

    path(
        "attendance/mark/",
        MarkAttendanceView.as_view()
    ),
    path("attendance/summary/", AttendanceSummaryView.as_view()),
    # Activity APIs

    path(
        "activity/create/",
        CreateActivityView.as_view()
    ),

    path(
        "activity/list/",
        ActivityListView.as_view()
    ),

    path(
        "activity/<int:activity_id>/",
        ActivityDetailView.as_view()
    ),

    path(
        "activity/update/<int:activity_id>/",
        UpdateActivityView.as_view()
    ),

    path(
        "activity/delete/<int:activity_id>/",
        DeleteActivityView.as_view()
    ),
    # Camp management
    path("camp/create/", CreateCampView.as_view()),
    path("camp/list/", CampListView.as_view()),
    path("camp/update/<int:camp_id>/", UpdateCampView.as_view()),
    path("camp/delete/<int:camp_id>/", DeleteCampView.as_view()),

    

    # Officer manages participants
    path("camp/participants/<int:camp_id>/", CampParticipantsView.as_view()),
    path("camp/participation/update/<int:participation_id>/",
         UpdateCampParticipationStatus.as_view()),

    path(
        "notices/",
        officer_views.list_notices
    ),

    path(
        "notice/create/",
        officer_views.create_notice
    ),
    path("notice/<int:id>/delete/", delete_notice),
path("notice/<int:id>/update/", update_notice),
path("feedbacks/", OfficerFeedbackListView.as_view()),

    # Poll
    path("poll/create/", CreatePollView.as_view()),
path("feedback/respond/", RespondFeedbackView.as_view()),
path("poll/results/<int:poll_id>/", PollResultView.as_view()),
path("ranks/", RankListView.as_view()),

path(
    "rank-vacancy/set/",
    SetRankVacancyView.as_view()
),

path(
    "rank-panel/create/",
    CreateRankPanelView.as_view()
),

path(
    "rank-panel/",
    RankPanelListView.as_view()
),
path("rank-vacancy/", RankVacancyListView.as_view()), # Use this for the list!
path("rank-vacancy/<int:pk>/", RankVacancyDetailView.as_view()),
path("rank-availability/", RankAvailabilityView.as_view()),
path("cadet/", CadetListView.as_view()),
path('reset-rank-panel/', ResetRankPanelView.as_view()),


path('reports/<int:pk>/review/', OfficerReportActionView.as_view(), name='report-review'),
path('reports/', OfficerReportListView.as_view(), name='officer-report-list'),
path('polls/<int:pk>/',PollDetailView.as_view(),name="poll_delete"),
path('polls/<int:pk>/',PollDetailView.as_view(),name="poll_delete"),
path('qr/generate/', CreateQRSessionView.as_view(), name='generate-qr'),

path(
        "notifications/delete-group/<str:group_id>/", 
        ManageNotificationView.as_view(), 
        name="delete-notification-group"
    ),
    path(
        "notifications/update-group/<str:group_id>/", 
        ManageNotificationView.as_view(), 
        name="update-notification-group"
    ),
    # Officer Endpoints
    # urls.py
path('inventory/manage/', OfficerInventoryView.as_view()), # For GET and POST
path('inventory/manage/<int:pk>/', OfficerInventoryView.as_view()), # For PATCH and DELETE
    # GET: List all pending cadet orders
    path('orders/all/', OfficerOrderReviewView.as_view(), name='orders-list'),
    
    # PATCH: Approve/Reject a specific order with a message
    path('orders/review/<int:order_id>/', OfficerOrderReviewView.as_view(), name='order-process'),
]