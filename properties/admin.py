from django.contrib import admin
from .models import Property, RentalRequest, Review, PropertyImage


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'property_type', 'price_per_month', 'location', 'is_available', 'created_at')
    list_filter = ('property_type', 'is_available', 'created_at')
    search_fields = ('title', 'location', 'owner__username')
    inlines = [PropertyImageInline]


@admin.register(RentalRequest)
class RentalRequestAdmin(admin.ModelAdmin):
    list_display = ('property', 'tenant', 'move_in_date', 'lease_duration_months', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('property__title', 'tenant__username')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('property', 'tenant', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('property__title', 'tenant__username', 'comment')
