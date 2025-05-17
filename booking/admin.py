from django.contrib import admin
from .models import AdminWorkingTime, Appointment

# Register AdminWorkingTime model
@admin.register(AdminWorkingTime)
class AdminWorkingTimeAdmin(admin.ModelAdmin):
    list_display = ('date', 'start_time', 'end_time')
    list_filter = ('date',)
    search_fields = ('date',)

# Register Appointment model
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'working_time', 'start_time', 'end_time', 'created_at')
    list_filter = ('working_time__date', 'user')
    search_fields = ('user__username', 'working_time__date')

