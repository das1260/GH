from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.http import JsonResponse
import threading

from django.contrib.auth.decorators import login_required
from users.models import UserProfile
from datetime import datetime, timedelta





def home(request):
    # if not request.user.is_authenticated:
    #     return redirect('signin')
    user1=request.user.is_authenticated
    return render(request, 'home.html',{'user1':user1})#, {'user': request.user})

def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = User.objects.get(username=email)
            if user.is_active:
                messages.error(request, 'Email is already registered. Please Login.')
                return redirect('login')
            else:
                # User exists but is inactive, resend confirmation link
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = token_generator.make_token(user)
                protocol = 'https' if request.is_secure() else 'http'  # Check if HTTPS
                domain = request.get_host()  # Get the domain with port if applicable
                confirmation_link = f'{protocol}://{domain}/confirm/{uid}/{token}/'

                def send_emails():
                    send_mail(
                    'Confirm your account',
                    f'Click on the link to confirm your account: {confirmation_link}',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                    
                threading.Thread(target=send_emails).start()

                
                messages.info(request, 'Your account is inactive. A new confirmation email has been sent.')
                return redirect('login')

        except User.DoesNotExist:
            # Create a new inactive user if not found
            user = User.objects.create_user(username=email, email=email, password=password, is_active=False)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator.make_token(user)
            protocol = 'https' if request.is_secure() else 'http'  # Check if HTTPS
            domain = request.get_host()  # Get the domain with port if applicable
            confirmation_link = f'{protocol}://{domain}/confirm/{uid}/{token}/'

            send_mail(
                'Activate your account with GhanAnand.in',
                f'To activate your account with GhanAnand.in please click on this link {confirmation_link}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            messages.success(request, 'A link has been sent to your email to activate your account')
            return redirect('confirm_email_link')

    return render(request, 'signup.html')
def confirm_email_link(request):
    return render(request, 'Link_Send.html')



def confirm_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)  # Automatically log the user in
        messages.success(request, 'Welcome! Your account has been activated, and you are now logged in.')
        return redirect('profile')  # Redirect to the profile page
    else:
        messages.error(request, 'The confirmation link is invalid or has expired.')
        return redirect('signup')
    

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None: 
            if user.is_active:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Please confirm your email address.')
                return redirect('login')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'login.html')

def signout(request):
    logout(request)
    return redirect('login')



@login_required
def profile_view(request):
    if request.user.is_authenticated:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        user1=request.user.is_authenticated
        if request.method == "POST":
            # Extracting form data from POST request
            profile.full_name = request.POST.get('name')
            profile.gender = request.POST.get('gender')
            try:
                profile.date_of_birth =  datetime.strptime(request.POST.get('dob'), "%d-%m-%Y").strftime("%Y-%m-%d")
            except:
                profile.date_of_birth =None

            try:
                time_of_birth=datetime.strptime(request.POST.get('time'), "%I:%M %p").strftime("%H:%M")
            except:
                time_of_birth=None

            profile.time_of_birth = time_of_birth
            profile.Country_of_Birth = request.POST.get('country')
            profile.Place_of_Birth = request.POST.get('birthplace')
            profile.country_code = request.POST.get('countrycode')
            profile.whatsapp = request.POST.get('whatsapp')
            if profile.date_of_birth == None:
                return render(request, 'profile.html',{'user1':user1,'profile':profile , "time_of_birth":time_of_birth,'message':'Enter your Date of Birth and Time of Birth'})
            elif time_of_birth ==  None:
                return render(request, 'profile.html',{'user1':user1,'profile':profile , "time_of_birth":time_of_birth,'message':'Enter your Date of Birth and Time of Birth'})
          
            else:
                profile.save()
                return redirect('home')  # Redirect to profile page after saving


        try:
            date_of_birth=datetime.strptime(str(profile.date_of_birth), "%Y-%m-%d").strftime("%d-%m-%Y")
        except:
            date_of_birth=None
        return render(request, 'profile.html',{'user1':user1,'profile':profile , 'date_of_birth':date_of_birth,"time_of_birth":profile.time_of_birth.strftime("%I:%M %p") if profile.time_of_birth else "Not Available"})    

    else:
        return redirect('login')