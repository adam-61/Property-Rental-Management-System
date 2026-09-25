from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Property(models.Model):
    PROPERTY_TYPES = (
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('studio', 'Studio'),
        ('condo', 'Condominium'),
        ('commercial', 'Commercial Space'),
    )

    FURNISHED_CHOICES = (
        ('unfurnished', 'Unfurnished'),
        ('semi_furnished', 'Semi-Furnished'),
        ('furnished', 'Fully Furnished'),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=200, verbose_name="Property Title")
    description = models.TextField(verbose_name="Description")
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES, default='apartment', verbose_name="Property Type")
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monthly Rent ($)")
    location = models.CharField(max_length=255, verbose_name="Location / Address")
    bedrooms = models.PositiveIntegerField(default=1, verbose_name="Bedrooms")
    bathrooms = models.PositiveIntegerField(default=1, verbose_name="Bathrooms")
    area_sqft = models.PositiveIntegerField(blank=True, null=True, verbose_name="Area (sq ft)")
    image = models.ImageField(upload_to='property_images/', blank=True, null=True, verbose_name="Property Image")
    is_available = models.BooleanField(default=True, verbose_name="Available for Rent")

    # House & Living Information
    furnished_status = models.CharField(max_length=30, choices=FURNISHED_CHOICES, default='unfurnished', blank=True, verbose_name="Furnishing Status")
    parking_info = models.CharField(max_length=120, blank=True, verbose_name="Parking Information", help_text="e.g. 2 Garage Spaces, Driveway, Street")
    pet_friendly = models.BooleanField(default=False, verbose_name="Pet Friendly")
    year_built = models.PositiveIntegerField(blank=True, null=True, verbose_name="Year Built")
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Security Deposit ($)")
    utilities_included = models.CharField(max_length=255, blank=True, verbose_name="Utilities Included", help_text="e.g. Water, Gas, Trash, WiFi")
    amenities = models.TextField(blank=True, verbose_name="House Amenities & Features", help_text="e.g. Central AC, Balcony, In-unit Laundry, Private Yard, Dishwasher")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Properties'

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return None

    @property
    def review_count(self):
        return self.reviews.count()

    def __str__(self):
        return f"{self.title} - ${self.price_per_month}/mo ({self.location})"


class RentalRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='rental_requests')
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rental_requests')
    move_in_date = models.DateField(verbose_name="Desired Move-In Date")
    lease_duration_months = models.PositiveIntegerField(default=12, verbose_name="Lease Duration (Months)")
    message = models.TextField(blank=True, verbose_name="Message / Introduction to Owner")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Request Status")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Request by {self.tenant.username} for {self.property.title} [{self.get_status_display()}]"


class Review(models.Model):
    RATING_CHOICES = (
        (5, '★★★★★ (5 - Excellent)'),
        (4, '★★★★☆ (4 - Very Good)'),
        (3, '★★★☆☆ (3 - Average)'),
        (2, '★★☆☆☆ (2 - Poor)'),
        (1, '★☆☆☆☆ (1 - Terrible)'),
    )

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Rating"
    )
    comment = models.TextField(verbose_name="Review Comment")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('property', 'tenant')

    def __str__(self):
        return f"{self.rating}★ Review by {self.tenant.username} for {self.property.title}"


class PropertyImage(models.Model):
    """Extra photos for a property's image gallery, in addition to the
    main `Property.image`. A property can have any number of these."""

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='property_gallery/', verbose_name="Gallery Photo")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']

    def __str__(self):
        return f"Gallery photo for {self.property.title}"
