from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import NCCHandbook, User
from .utils import extract_and_save_pdf_content


class CustomUserAdmin(UserAdmin):
    model = User

    list_display = ('email', 'name', 'role', 'is_staff', 'is_approved')
    list_filter = ('role', 'is_staff', 'is_approved')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('role', 'is_staff', 'is_active', 'is_superuser', 'is_approved')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'role', 'is_staff', 'is_active'),
        }),
    )

    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(User, CustomUserAdmin)

from .models import (
    CadetProfile,
    PersonalDetails,
    AcademicDetails,
    BankDetails,
    IdentityDetails,
    MedicalDetails,
    Document,
    Activity,
    Attendance
)

admin.site.register(CadetProfile)
admin.site.register(PersonalDetails)
admin.site.register(AcademicDetails)
admin.site.register(BankDetails)
admin.site.register(IdentityDetails)
admin.site.register(MedicalDetails)
admin.site.register(Document)

@admin.register(NCCHandbook)
class NCCHandbookAdmin(admin.ModelAdmin):
    actions = ['re_extract_text']

    @admin.action(description='Re-extract text from selected PDFs')
    def re_extract_text(self, request, queryset):
        for obj in queryset:
            extract_and_save_pdf_content(obj.id)
        self.message_user(request, "Text extraction complete for selected books.")


admin.site.register(Activity)
admin.site.register(Attendance)