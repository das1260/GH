from django import forms
from users.models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'date_of_birth', 'time_of_birth', 'gender', 'birth_location']
    
    # Customizing the date field to show a calendar
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}), 
        input_formats=['%Y-%m-%d']
    )
    
    # Customizing the time field to show a time picker
    time_of_birth = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}), 
        input_formats=['%H:%M:%S']
    )

    # Customizing the gender field as a dropdown
    GENDER_CHOICES = [
        ('', 'Select Gender'),  # Empty option for prompt
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),  # Optional styling class
        required=True
    )
