from rest_framework import serializers
from .models import CampParticipation, Feedback, NCCHandbook, Poll, PollOption, PollVote, Report, UniformItem, User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    CadetProfile,
    PersonalDetails,
    AcademicDetails,
    BankDetails,
    IdentityDetails,
    MedicalDetails,
    Document,
    Attendance,
    Camp,
    
    
)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'name']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role='CADET',
            name=validated_data['name']
        )
        user.is_approved = False
        user.save()
        

        # Send Email to Admin
        send_mail(
            subject="New Cadet Registration Request",
            message=f"""
New cadet has registered.

Name: {user.name}
Email: {user.email}


Please login to admin panel to approve.
""",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )

        return user
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):

        email = data.get("email")
        password = data.get("password")

        # Step 1: get user by email
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")

        # Step 2: authenticate properly
        user = authenticate(
            username=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        # Step 3: approval check
        if not user.is_approved:
            raise serializers.ValidationError(
                "Your account is waiting for admin approval"
            )

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "email": user.email,
            "role": user.role,
            "is_approved": user.is_approved,
            "profile_completed": user.profile_completed,
        } 

# ===============================
# 1️⃣ CADET PROFILE SERIALIZER
# ===============================

class CadetProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = CadetProfile
        exclude = ['user']

    read_only_fields = [
            'edit_permission_granted',
            'profile_editable_until',
            'correction_requested',
        ]

    # ===============================
    # CREATE PROFILE
    # ===============================
    def create(self, validated_data):
        user = self.context['request'].user

        if hasattr(user, 'cadet_profile'):
            raise serializers.ValidationError(
                "Cadet profile already exists."
            )

        return CadetProfile.objects.create(
            user=user,
            **validated_data
        )

    # ===============================
    # UPDATE PROFILE (EDIT CONTROL)
    # ===============================
    def update(self, instance, validated_data):

        if not instance.can_edit():
            raise serializers.ValidationError(
                "Edit window expired. Request correction approval."
            )

        return super().update(instance, validated_data)

    # ===============================
    # RETURN CAN_EDIT BOOLEAN
    # ===============================
    def get_can_edit(self, obj):
        return obj.can_edit()

# ===============================
# 2️⃣ PERSONAL DETAILS
# ===============================

class PersonalDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PersonalDetails
        exclude = ['user']

    def create(self, validated_data):
        user = self.context['request'].user

        if hasattr(user, 'personal_details'):
            raise serializers.ValidationError("Personal details already submitted.")

        return PersonalDetails.objects.create(user=user, **validated_data)


# ===============================
# 3️⃣ ACADEMIC DETAILS
# ===============================

class AcademicDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = AcademicDetails
        exclude = ['user']

    def create(self, validated_data):
        user = self.context['request'].user

        if hasattr(user, 'academic_details'):
            raise serializers.ValidationError("Academic details already submitted.")

        return AcademicDetails.objects.create(user=user, **validated_data)


# ===============================
# 4️⃣ BANK DETAILS
# ===============================

class BankDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = BankDetails
        exclude = ['user']

    def create(self, validated_data):
        user = self.context['request'].user

        if hasattr(user, 'bank_details'):
            raise serializers.ValidationError("Bank details already submitted.")

        return BankDetails.objects.create(user=user, **validated_data)


# ===============================
# 5️⃣ IDENTITY DETAILS
# ===============================

class IdentityDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = IdentityDetails
        exclude = ['user']

    def create(self, validated_data):
        user = self.context['request'].user

        if hasattr(user, 'identity_details'):
            raise serializers.ValidationError("Identity details already submitted.")

        return IdentityDetails.objects.create(user=user, **validated_data)


# ===============================
# 6️⃣ MEDICAL DETAILS
# ===============================

class MedicalDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = MedicalDetails
        exclude = ['user']

    def create(self, validated_data):
        user = self.context['request'].user

        if hasattr(user, 'medical_details'):
            raise serializers.ValidationError("Medical details already submitted.")

        medical = MedicalDetails.objects.create(user=user, **validated_data)

        # Mark profile completed after final step
        user.profile_completed = True
        user.save()

        return medical


# ===============================
# 7️⃣ DOCUMENT UPLOAD
# ===============================

class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = ['id', 'document_type', 'file', 'uploaded_at']
        read_only_fields = ['uploaded_at']

    def create(self, validated_data):
        validated_data.pop('user', None)   # remove if exists
        user = self.context['request'].user
        return Document.objects.create(user=user, **validated_data)
    
class ProfileStatusSerializer(serializers.Serializer):

    profile_completed = serializers.BooleanField()
    cadet_profile = serializers.BooleanField()
    personal_details = serializers.BooleanField()
    academic_details = serializers.BooleanField()
    bank_details = serializers.BooleanField()
    identity_details = serializers.BooleanField()
    medical_details = serializers.BooleanField()

class CadetCampSerializer(serializers.ModelSerializer):
    # Including the helper methods from your model
    seats_left = serializers.IntegerField(read_only=True)
    is_applied = serializers.SerializerMethodField()

    class Meta:
        model = Camp
        fields = [
            'id', 'title', 'total_seats', 'camp_type', 
            'location', 'start_date', 'end_date', 'seats_left', 'is_applied'
        ]

    def get_is_applied(self, obj):
        # Checks if the requesting cadet has already shown interest
        user = self.context.get('request').user
        return CampParticipation.objects.filter(camp=obj, cadet=user).exists()




class AttendanceSerializer(serializers.ModelSerializer):
    # Pull data from the related Activity model
    activity_title = serializers.CharField(source='activity.title', read_only=True)
    activity_type = serializers.CharField(source='activity.activity_type', read_only=True)
    
    # Format the date for the frontend
    marked_at_formatted = serializers.DateTimeField(
        source='marked_at', format="%d %b %Y, %I:%M %p", read_only=True
    )

    class Meta:
        model = Attendance
        fields = [
            'id', 'activity_title', 'activity_type', 
            'status', 'marked_at_formatted', 'marked_at'
        ]

class ReportSerializer(serializers.ModelSerializer):
    # Change this line to use a SerializerMethodField for a smart fallback
    generated_by_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Report
        fields = [
            'id', 'title', 'report_type', 'event_date', 'location', 
            'file', 'status', 'status_display', 'officer_remarks', 
            'generated_by', 'generated_by_name', 'generated_at'
        ]
        read_only_fields = ['status', 'officer_remarks', 'generated_by', 'generated_at']

    # This function checks if full_name exists; if not, it uses the username
    def get_generated_by_name(self, obj):
    # Check if the user object exists
        if obj.generated_by:
            # Return the 'name' field from your Custom User model
            # If 'name' is empty, fallback to the email
            return obj.generated_by.name if obj.generated_by.name else obj.generated_by.email
        
        return "Unknown Cadet"

    def create(self, validated_data):
        # Ensure the user is injected from the request context
        validated_data['generated_by'] = self.context['request'].user
        return super().create(validated_data)

class PollOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollOption
        fields = ['id', 'option_text']

class PollSerializer(serializers.ModelSerializer):
    options = PollOptionSerializer(many=True, read_only=True)
    has_voted = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = ['id', 'question', 'options', 'is_active', 'created_at', 'has_voted']

    def get_has_voted(self, obj):
        user = self.context['request'].user
        return PollVote.objects.filter(poll=obj, cadet=user).exists()
    



class NCCHandbookSerializer(serializers.ModelSerializer):
    # This ensures the full URL (http://127.0.0.1:8000/media/...) is sent to Flutter
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = NCCHandbook
        fields = ['id', 'title', 'category', 'file', 'file_url', 'uploaded_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None

class QRScanSerializer(serializers.Serializer):
    qr_code = serializers.CharField(required=True)

class CadetFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'subject', 'message', 'status', 'created_at', 'response']
        read_only_fields = ['status', 'created_at', 'response']


from rest_framework import serializers
from .models import UniformItem, UniformOrder, OrderItem
from django.db import transaction

class UniformItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniformItem
        fields = ['id', 'name', 'item_type', 'price', 'image', 'available_quantity']

class OrderItemCreateSerializer(serializers.ModelSerializer):
    # This is used for input: item ID and how many they want
    item_id = serializers.IntegerField()

    class Meta:
        model = OrderItem
        fields = ['item_id', 'quantity']

class CadetOrderSerializer(serializers.ModelSerializer):
    # This accepts a list of items
    items = OrderItemCreateSerializer(many=True)

    class Meta:
        model = UniformOrder
        fields = ['payment_method', 'items']

    # Inside CadetOrderSerializer.create
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        
        with transaction.atomic(): # Ensures database integrity
            order = UniformOrder.objects.create(cadet=user, status='PENDING', **validated_data)
            total_price = 0
            
            for item_data in items_data:
                inventory_item = UniformItem.objects.get(id=item_data['item_id'])
                
                # Stock Validation check
                if inventory_item.available_quantity < item_data['quantity']:
                    raise serializers.ValidationError(f"Not enough stock for {inventory_item.name}")

                OrderItem.objects.create(
                    order=order,
                    item=inventory_item,
                    quantity=item_data['quantity'],
                    price_at_order=inventory_item.price
                )
                total_price += (inventory_item.price * item_data['quantity'])
                
            order.total_amount = total_price
            order.save()
        return order