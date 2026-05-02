
from django.urls import include, path
from .views import *
from .dashboard_views import CadetDashboardView
from accounts import views
from .officer_views import CadetListView

urlpatterns = [
    
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/cadet/', CadetProfileView.as_view()),
    path('profile/personal/', PersonalDetailsView.as_view()),
    path('profile/academic/', AcademicDetailsView.as_view()),
    path('profile/bank/', BankDetailsView.as_view()),
    path('profile/identity/', IdentityDetailsView.as_view()),
    path('profile/medical/', MedicalDetailsView.as_view()),
    path('profile/document/', DocumentUploadView.as_view()),
    path('profile/status/', ProfileStatusView.as_view()),
    path('dashboard/cadet/', CadetDashboardView.as_view(), name='cadet-dashboard'),
    path("complete-profile/", CompleteProfileView.as_view()),
    path("dashboard/", CadetDashboardView.as_view()),
    #path("ai/ask/", AIAssistantView.as_view()),
    
    path("profile/full/", FullCadetProfileView.as_view(), name="full-profile"),
    path("officer/", include("accounts.officer_urls")),
    path(
        "profile/request-correction/",
        RequestCorrectionView.as_view(),
        name="request-correction"
    ),
    path(
        "profile/cadet/",
        CadetProfileUpdateView.as_view()
    ),

    path(
        "profile/personal/",
        PersonalDetailsUpdateView.as_view()
    ),

    path(
        "profile/academic/",
        AcademicDetailsUpdateView.as_view()
    ),

    path(
        "profile/bank/",
        BankDetailsUpdateView.as_view()
    ),

    path(
        "profile/identity/",
        IdentityDetailsUpdateView.as_view()
    ),

    path(
        "profile/medical/",
        MedicalDetailsUpdateView.as_view()
    ),

    path(
        "profile/photo/",
        ProfilePhotoUploadView.as_view()
    ),
    path(
    "notifications/",
    views.list_notifications
),
path("cadet/feedback/submit/", SubmitFeedbackView.as_view()),
path("polls/active/", ActivePollListView.as_view()),
path("polls/vote/", VotePollView.as_view()),
path(
        "notifications/",
        UserNotificationListView.as_view(),
        name="notifications"
    ),

    path(
        "notifications/read/<int:notification_id>/",
        MarkNotificationReadView.as_view(),
        name="mark-notification-read"
    ),

    path(
        "notifications/unread-count/",
        UnreadNotificationCountView.as_view(),
        name="unread-notification-count"
    ),
    # path('inventory/', InventoryListView.as_view(), name='inventory-list'),
    
    # # Post a new request (Selection)
    # path('request/create/', UniformRequestCreateView.as_view(), name='request-create'),
    
    # # Get the list of requests (to show the Bill tab)
    # path('my-requests/', CadetRequestListView.as_view(), name='my-requests'),

    path('cadet/camp/list/', views.cadet_camp_list, name='cadet-camp-list'),
    path('cadet/camp/interest/', views.cadet_show_interest, name='cadet-camp-interest'),
    path('cadet/attendance-stats/', CadetAttendanceDetailView.as_view(), name='cadet-attendance-stats'),
    path('reports/', CadetReportListView.as_view(), name='report-list-upload'),
    path('ai/chat/', NCCChatBotView.as_view(), name='ncc-ai-chat'),
    path('materials/', StudyMaterialListCreateView.as_view(), name='material-list-create'),
    path('qr/scan/', ScanQRAttendanceView.as_view(), name='scan-qr'),
    # Cadet Endpoints
    path('cadet/inventory/', views.CadetInventoryListView.as_view(), name='cadet-inventory'),
    path('cadet/order/place/', views.PlaceOrderView.as_view(), name='place-order'),
    path('orders/my-bills/', views.MyBillsListView.as_view(), name='view-bills'), # You'd need a list view for this
]   