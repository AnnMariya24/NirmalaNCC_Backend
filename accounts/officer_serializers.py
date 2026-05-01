from datetime import timedelta,date


from .models import NCCHandbook, QRAttendanceSession
from rest_framework import serializers
from .models import (
    CadetProfile,
    Camp,
    CampParticipation,
    Feedback,
    Notice,
    Notification,
    PersonalDetails,
    AcademicDetails,
    BankDetails,
    IdentityDetails,
    MedicalDetails,
    Attendance,
    Activity,
    Poll,
    PollOption,
    Rank,
    RankPanel,
    RankPanel,
    RankVacancy
)


# ===============================
# SUB SERIALIZERS
# ===============================

class PersonalDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PersonalDetails
        fields = "__all__"


class AcademicDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = AcademicDetails
        fields = "__all__"


class BankDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = BankDetails
        fields = "__all__"


class IdentityDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = IdentityDetails
        fields = "__all__"


class MedicalDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = MedicalDetails
        fields = "__all__"


# ===============================
# CADET CORE SERIALIZER
# ===============================
    
class OfficerCadetSerializer(serializers.ModelSerializer):

    name = serializers.CharField(source="user.name", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    is_approved = serializers.BooleanField(source="user.is_approved", read_only=True)

    personal_details = PersonalDetailsSerializer(
        source="user.personal_details",
        read_only=True
    )

    academic_details = AcademicDetailsSerializer(
        source="user.academic_details",
        read_only=True
    )

    bank_details = BankDetailsSerializer(
        source="user.bank_details",
        read_only=True
    )

    identity_details = IdentityDetailsSerializer(
        source="user.identity_details",
        read_only=True
    )

    medical_details = MedicalDetailsSerializer(
        source="user.medical_details",
        read_only=True
    )

    class Meta:
        model = CadetProfile
        fields = [
            "id",
            "name",
            "email",
            "cadet_number",
            "training_year",
            "wing",
            "division",
            "blood_group",
            "profile_photo",
            "previously_in_ncc",
            "previous_ncc_institution",
            "previous_ncc_certificate",
            "is_approved",
            "personal_details",
            "academic_details",
            "bank_details",
            "identity_details",
            "medical_details",
        ]

class AttendanceSerializer(serializers.ModelSerializer):

    cadet_name = serializers.CharField(
        source="cadet.user.name",
        read_only=True
    )

    cadet_number = serializers.CharField(
        source="cadet.cadet_number",
        read_only=True
    )

    class Meta:
        model = Attendance
        fields = [
            "id",
            "cadet",
            "cadet_name",
            "cadet_number",
            "activity",
            "status",
            "marked_by",
            "marked_at"
        ]

class AttendanceCadetSerializer(serializers.ModelSerializer):

    name = serializers.CharField(source="user.name")

    class Meta:
        model = CadetProfile
        fields = [
            "id",
            "name",
            "cadet_number",
            "division",
            "training_year"
        ]

class ActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Activity
        fields = "__all__"
        read_only_fields = ["id", "created_by", "created_at"]

    def validate_date(self, value):

        today = date.today()

        # allow only today or last 24 days
        if value < today - timedelta(days=24):
            raise serializers.ValidationError(
                "Activity date can only be within the last 24 days."
            )

        if value > today:
            raise serializers.ValidationError(
                "Future dates are not allowed."
            )

        return value
    
class CampSerializer(serializers.ModelSerializer):

    approved_count = serializers.SerializerMethodField()
    seats_left = serializers.SerializerMethodField()

    class Meta:
        model = Camp
        fields = "__all__"
        read_only_fields = ["created_by", "created_at"]

    def get_approved_count(self, obj):
        return obj.participants.filter(status="APPROVED").count()

    def get_seats_left(self, obj):
        approved = obj.participants.filter(status="APPROVED").count()
        return obj.total_seats - approved
    
class CampParticipationSerializer(serializers.ModelSerializer):

    cadet_name = serializers.CharField(
        source="cadet.name",
        read_only=True
    )

    camp_title = serializers.CharField(
        source="camp.title",
        read_only=True
    )

    class Meta:
        model = CampParticipation
        fields = "__all__"
        read_only_fields = ["applied_at"]
    
class NoticeSerializer(serializers.ModelSerializer):

    created_by_name = serializers.CharField(
        source="created_by.name",
        read_only=True
    )

    class Meta:
        model = Notice
        fields = "__all__"
         # These fields should not be sent from Flutter
        read_only_fields = [
            "created_by",
            "created_at",
            "is_active"
        ]

class FeedbackSerializer(serializers.ModelSerializer):

    cadet_name = serializers.CharField(source="cadet.name", read_only=True)

    class Meta:
        model = Feedback
        fields = "__all__"
        read_only_fields = [
            "cadet",
            "status",
            "response",
            "responded_by",
            "created_at",
            "responded_at"
        ]


# =========================
# POLL OPTION SERIALIZER
# =========================

class PollOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = PollOption
        fields = ["id", "option_text"]


# =========================
# POLL SERIALIZER
# =========================

class PollSerializer(serializers.ModelSerializer):
    options = PollOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Poll
        fields = ['id', 'question', 'options', 'created_at', 'is_active']

class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "notification_type",
            "is_read",
            "created_at"
        ]
class RankSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rank
        fields = "__all__"

class RankVacancySerializer(serializers.ModelSerializer):

    class Meta:
        model = RankVacancy
        fields = "__all__"

class RankPanelSerializer(serializers.ModelSerializer):

    cadet_name = serializers.CharField(source="cadet.name", read_only=True)
    rank_name = serializers.CharField(source="rank.name", read_only=True)

    class Meta:
        model = RankPanel
        fields = [
            "id",
            "cadet",
            "cadet_name",
            "rank",
            "rank_name",
            "year",
        ]

# from rest_framework import serializers
# from .models import InventoryItem, UniformOrder, OrderItem

# class InventoryItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = InventoryItem
#         fields = '__all__'

# class OrderItemSerializer(serializers.ModelSerializer):
#     item_name = serializers.ReadOnlyField(source='item.name')
    
#     class Meta:
#         model = OrderItem
#         fields = ['id', 'item', 'item_name', 'quantity', 'price_at_order']

# class UniformOrderSerializer(serializers.ModelSerializer):
#     items = OrderItemSerializer(many=True, read_only=True)
#     cadet_name = serializers.ReadOnlyField(source='cadet.username')

#     class Meta:
#         model = UniformOrder
#         fields = ['id', 'cadet', 'cadet_name', 'status', 'payment_method', 'total_amount', 'items', 'created_at']


class NCCHandbookSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = NCCHandbook
        fields = ['id', 'title', 'category', 'file', 'file_url', 'uploaded_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None
    
class QRAttendanceSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRAttendanceSession
        fields = ['id', 'activity', 'qr_code', 'valid_from', 'valid_until', 'is_active']
        read_only_fields = ['qr_code', 'is_active']

from rest_framework import serializers
from .models import UniformItem, UniformOrder, OrderItem

class UniformItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniformItem
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')
    class Meta:
        model = OrderItem
        fields = ['item_name', 'quantity', 'price_at_order', 'get_cost']

class UniformOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    cadet_name = serializers.ReadOnlyField(source='cadet.get_full_name')

    class Meta:
        model = UniformOrder
        fields = ['id', 'cadet_name', 'status', 'payment_method', 'total_amount', 'items', 'officer_note', 'created_at']