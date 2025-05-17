from django.db import models
from django.contrib.auth.models import User

class AdminWorkingTime(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.date} {self.start_time} - {self.end_time}"

class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    working_time = models.ForeignKey(AdminWorkingTime, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    payment_status = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    Booking_Fee= models.CharField(max_length=5, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment by {self.user.username} on {self.working_time.date} from {self.start_time} to {self.end_time}"
