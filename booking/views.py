from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, timedelta, time
from .models import AdminWorkingTime, Appointment
from razorpay import Client
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
import threading

import os
from dotenv import load_dotenv

load_dotenv()

client = Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Helper function to generate slots
def get_available_slots(working_time, duration_td):
    slots = []
    now = datetime.now()  # Get the current datetime

    # Combine date and time to create datetime objects
    current = datetime.combine(working_time.date, working_time.start_time)
    end_dt = datetime.combine(working_time.date, working_time.end_time)

    # If the working date is today, adjust `current` to exclude past time slots
    if working_time.date == now.date():
        current = max(current, now)

    while current + duration_td <= end_dt:
        slot_start = current.time()
        slot_end = (current + duration_td).time()

        # Check for conflicts with already booked appointments
        conflict = Appointment.objects.filter(
            working_time=working_time,
            start_time__lt=slot_end,
            end_time__gt=slot_start
        ).exists()

        if not conflict:
            slots.append((slot_start.strftime("%H:%M"), slot_end.strftime("%H:%M")))

        current += duration_td

    return slots


def book_appointment(request):
    if not request.user.is_authenticated:
        
        return redirect('signup')  # Redirect to login page



    available_slots = []
    working_time = None
    selected_date = request.GET.get('date')
    selected_duration = request.GET.get('duration')

    if selected_date and selected_duration:
        try:
            working_time = AdminWorkingTime.objects.get(date=selected_date)
        except AdminWorkingTime.DoesNotExist:
            messages.error(request, "Sorry, it's already taken")
        if working_time:
            duration_map = {
                "15": timedelta(minutes=15),
                "30": timedelta(minutes=30),
                "45": timedelta(minutes=45)
            }
            duration_td = duration_map.get(selected_duration, timedelta(minutes=15))
            available_slots = get_available_slots(working_time, duration_td)

    # Handle booking when user submits a chosen slot
    if request.method == 'POST':
        slot_value = request.POST.get('slot')
        if not working_time or not slot_value:
            messages.error(request, "Please select a valid slot.")
        else:
            slot_start_str, slot_end_str = slot_value.split('-')
            # Double-check that the slot is still available before booking.
            conflict = Appointment.objects.filter(
                working_time=working_time,
                start_time__lt=slot_end_str,
                end_time__gt=slot_start_str
            ).exists()
            if conflict:
                messages.error(request, "Sorry, it's already taken")
            else:
                # Create Razorpay order
                amount=int(selected_duration)*15*100
                order = client.order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': '1'
        })
                context = {
        'selected_date': selected_date,
        'working_time': working_time,
        'start_time': slot_start_str,
        'end_time': slot_end_str,
        'duration': selected_duration,
        'order_id': order['id'],
        'amount': amount,
        'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID,
        'Booking_Fee':amount/100
        
    }
                return render(request, 'booking/payment.html',context)

    # Compute minimum (today) and maximum booking date (today + 15 days)
    today = datetime.today().date()
    max_date = today + timedelta(days=15)

    context = {
        'available_slots': available_slots,
        'today': today.isoformat(),
        'max_date': max_date.isoformat(),
    }
    return render(request, 'booking/appointment.html', context)

def confirm_payment(request):
    if request.method == 'POST':
        # Retrieve POST data
        selected_date = request.POST.get('selected_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        working_time = request.POST.get('working_time')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        Booking_Fee = request.POST.get('Booking_Fee')

        # Use select_related to minimize database hits if needed
        working_time = AdminWorkingTime.objects.select_related().get(date=selected_date)

        # Save the appointment
        appointment = Appointment(
            user=request.user,
            working_time=working_time,
            start_time=start_time,
            end_time=end_time,
            payment_status=True,
            Booking_Fee=Booking_Fee,
            payment_id=razorpay_order_id
        )
        appointment.save()

        # Email details
        user_email = request.user.email
        admin_email = os.getenv("admin_email")  # Replace with actual admin email
        subject = 'Your appointment with GhanAnand.in is confirmed'
        
        profile = request.user.profile
        # User message
        user_message = (

            f"Dear Mr./Ms. {profile.full_name},\n\n"
            f"Your appointment is confirmed! Date:{selected_date}  and Time: {start_time} to {end_time} hrs.\n"
            f"Payment ID:  {razorpay_order_id}\n"
            "You will receive a G-meet link to connect with GhanAnand for consultation.\n"
            "Thank You!"
        )
        
        # Admin message (minimized redundant access)
    
        admin_message = (
            f"New appointment booked by {request.user.get_full_name()} ({request.user.email}).\n\n"
            f"Date: {selected_date}\nStart Time: {start_time}\nEnd Time: {end_time}\n"
            f"Payment ID: {razorpay_order_id}\n\n"
            f"User Profile Details:\n"
            f"User Name: {profile.full_name}\n"
            f"Gender: {profile.gender}\n"
            f"Date Of Birth: {profile.date_of_birth}\n"
            f"Time Of Birth: {profile.time_of_birth}\n"
            f"Country Of Birth: {profile.Country_of_Birth}\n"
            f"Place Of Birth: {profile.Place_of_Birth}\n"
            f"Email: {request.user.email}\n"
            f"WhatsApp: {profile.country_code, profile.whatsapp if hasattr(request.user, 'profile') else 'N/A'}\n"
        )

        # Asynchronous email sending using threading
        def send_emails():
            send_mail(subject, user_message, 'no-reply@example.com', [user_email])
            send_mail('New Appointment Booked', admin_message, 'no-reply@example.com', [admin_email])

        threading.Thread(target=send_emails).start()

        return redirect('appointment_success')




def appointment_success(request):
    return render(request, 'booking/success.html')


def test(request):
    user_email = request.user.profile.full_name
    print(user_email)
    return redirect('home')