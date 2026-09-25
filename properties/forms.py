from django import forms
from .models import Property, RentalRequest, Review


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title', 'property_type', 'price_per_month', 'location',
            'bedrooms', 'bathrooms', 'area_sqft', 'description', 'image', 'is_available',
            'furnished_status', 'parking_info', 'pet_friendly', 'year_built',
            'security_deposit', 'utilities_included', 'amenities'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Modern Sunset Apartment', 'class': 'form-input'}),
            'property_type': forms.Select(attrs={'class': 'form-input'}),
            'price_per_month': forms.NumberInput(attrs={'placeholder': '1500.00', 'step': '0.01', 'class': 'form-input'}),
            'location': forms.TextInput(attrs={'placeholder': 'City, State, Neighborhood', 'class': 'form-input'}),
            'bedrooms': forms.NumberInput(attrs={'min': '0', 'class': 'form-input'}),
            'bathrooms': forms.NumberInput(attrs={'min': '0', 'class': 'form-input'}),
            'area_sqft': forms.NumberInput(attrs={'placeholder': 'e.g. 1200', 'min': '0', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe property features, nearby amenities, parking, utilities, etc.', 'class': 'form-input form-textarea'}),
            'image': forms.FileInput(attrs={'class': 'form-file-input', 'accept': 'image/*'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'furnished_status': forms.Select(attrs={'class': 'form-input'}),
            'parking_info': forms.TextInput(attrs={'placeholder': 'e.g. 2 Garage Spaces, Driveway, Street Parking', 'class': 'form-input'}),
            'pet_friendly': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'year_built': forms.NumberInput(attrs={'placeholder': 'e.g. 2021', 'min': '1800', 'max': '2100', 'class': 'form-input'}),
            'security_deposit': forms.NumberInput(attrs={'placeholder': 'e.g. 1500.00', 'step': '0.01', 'class': 'form-input'}),
            'utilities_included': forms.TextInput(attrs={'placeholder': 'e.g. Water, Gas, Trash, WiFi', 'class': 'form-input'}),
            'amenities': forms.Textarea(attrs={'rows': 3, 'placeholder': 'e.g. Central Air Conditioning, Private Balcony, In-unit Washer/Dryer, Swimming Pool, Gym', 'class': 'form-input form-textarea'}),
        }


class RentalRequestForm(forms.ModelForm):
    class Meta:
        model = RentalRequest
        fields = ['move_in_date', 'lease_duration_months', 'message']
        widgets = {
            'move_in_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'lease_duration_months': forms.NumberInput(attrs={'min': '1', 'max': '60', 'class': 'form-input', 'placeholder': '12'}),
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Introduce yourself, occupation, preferred move-in terms...', 'class': 'form-input form-textarea'}),
        }


class PropertySearchForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search by title, amenities...', 'class': 'form-input'}))
    location = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'City or location...', 'class': 'form-input'}))
    property_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Property Types')] + list(Property.PROPERTY_TYPES),
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    furnished_status = forms.ChoiceField(
        required=False,
        choices=[('', 'Any Furnishing')] + list(Property.FURNISHED_CHOICES),
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    min_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Min Rent ($)', 'class': 'form-input'}))
    max_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Max Rent ($)', 'class': 'form-input'}))
    bedrooms = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Min Beds', 'class': 'form-input'}))
    pet_friendly = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}))


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-input'}),
            'comment': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Share your experience renting this property...',
                'class': 'form-input form-textarea'
            }),
        }
