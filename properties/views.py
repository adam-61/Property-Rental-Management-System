from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from accounts.decorators import owner_required, tenant_required
from .models import Property, RentalRequest, Review, PropertyImage
from .forms import PropertyForm, RentalRequestForm, PropertySearchForm, ReviewForm


# ==============================================================================
# Public & Tenant Views
# ==============================================================================

def property_list_view(request):
    form = PropertySearchForm(request.GET or None)
    properties = Property.objects.filter(is_available=True)

    if form.is_valid():
        q = form.cleaned_data.get('q')
        location = form.cleaned_data.get('location')
        property_type = form.cleaned_data.get('property_type')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        bedrooms = form.cleaned_data.get('bedrooms')

        furnished_status = form.cleaned_data.get('furnished_status')
        pet_friendly = form.cleaned_data.get('pet_friendly')

        if q:
            properties = properties.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(amenities__icontains=q))
        if location:
            properties = properties.filter(location__icontains=location)
        if property_type:
            properties = properties.filter(property_type=property_type)
        if furnished_status:
            properties = properties.filter(furnished_status=furnished_status)
        if pet_friendly:
            properties = properties.filter(pet_friendly=True)
        if min_price is not None:
            properties = properties.filter(price_per_month__gte=min_price)
        if max_price is not None:
            properties = properties.filter(price_per_month__lte=max_price)
        if bedrooms is not None:
            properties = properties.filter(bedrooms__gte=bedrooms)

    context = {
        'properties': properties,
        'form': form,
        'total_count': properties.count()
    }
    return render(request, 'properties/property_list.html', context)


def property_detail_view(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    gallery_images = prop.gallery_images.all()
    user_request = None
    has_reviewed = False
    can_review = False

    if request.user.is_authenticated:
        user_request = RentalRequest.objects.filter(property=prop, tenant=request.user).first()
        profile = getattr(request.user, 'profile', None)
        if profile and profile.is_tenant:
            has_reviewed = Review.objects.filter(property=prop, tenant=request.user).exists()
            has_accepted_request = RentalRequest.objects.filter(
                property=prop, tenant=request.user, status='accepted'
            ).exists()
            can_review = has_accepted_request and not has_reviewed

    context = {
        'property': prop,
        'gallery_images': gallery_images,
        'user_request': user_request,
        'review_form': ReviewForm() if can_review else None,
        'can_review': can_review,
        'has_reviewed': has_reviewed,
    }
    return render(request, 'properties/property_detail.html', context)


@tenant_required
def send_request_view(request, pk):
    prop = get_object_or_404(Property, pk=pk)

    if prop.owner == request.user:
        messages.error(request, "You cannot send a rental request for your own property.")
        return redirect('property_detail', pk=prop.pk)

    if not prop.is_available:
        messages.error(request, "This property is currently not available for rent.")
        return redirect('property_detail', pk=prop.pk)

    # Check for existing pending or accepted request
    existing_request = RentalRequest.objects.filter(
        property=prop,
        tenant=request.user,
        status__in=['pending', 'accepted']
    ).first()

    if existing_request:
        messages.info(request, f"You already have a {existing_request.get_status_display()} request for this property.")
        return redirect('my_requests')

    if request.method == 'POST':
        form = RentalRequestForm(request.POST)
        if form.is_valid():
            rental_req = form.save(commit=False)
            rental_req.property = prop
            rental_req.tenant = request.user
            rental_req.status = 'pending'
            rental_req.save()
            messages.success(request, f"Rental request for '{prop.title}' has been submitted successfully to the owner!")
            return redirect('my_requests')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = RentalRequestForm()

    return render(request, 'properties/send_request.html', {'form': form, 'property': prop})


@tenant_required
def my_requests_view(request):
    requests_list = RentalRequest.objects.filter(tenant=request.user).select_related('property', 'property__owner')
    return render(request, 'properties/my_requests.html', {'requests_list': requests_list})


@tenant_required
def cancel_request_view(request, pk):
    rental_req = get_object_or_404(RentalRequest, pk=pk, tenant=request.user)

    if rental_req.status != 'pending':
        messages.error(request, f"You can only cancel pending requests. Current status is {rental_req.get_status_display()}.")
        return redirect('my_requests')

    if request.method == 'POST':
        rental_req.status = 'cancelled'
        rental_req.save()
        messages.success(request, f"Your rental request for '{rental_req.property.title}' has been cancelled.")
        return redirect('my_requests')

    return render(request, 'properties/cancel_request_confirm.html', {'rental_req': rental_req})


@tenant_required
def add_review_view(request, pk):
    prop = get_object_or_404(Property, pk=pk)

    # A tenant may only review a property once their rental request for it
    # has been accepted by the owner.
    has_accepted_request = RentalRequest.objects.filter(
        property=prop, tenant=request.user, status='accepted'
    ).exists()

    if not has_accepted_request:
        messages.error(request, "You can only review a property after one of your rental requests for it has been accepted.")
        return redirect('property_detail', pk=prop.pk)

    # A tenant can review a given property only once.
    if Review.objects.filter(property=prop, tenant=request.user).exists():
        messages.info(request, "You have already reviewed this property.")
        return redirect('property_detail', pk=prop.pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.property = prop
            review.tenant = request.user
            review.save()
            messages.success(request, "Thank you! Your review has been posted.")
            return redirect('property_detail', pk=prop.pk)
        else:
            messages.error(request, "Please correct the errors in your review.")
    else:
        form = ReviewForm()

    return render(request, 'properties/add_review.html', {'form': form, 'property': prop})


# ==============================================================================
# Property Owner Views
# ==============================================================================

@owner_required
def my_properties_view(request):
    properties = Property.objects.filter(owner=request.user)
    return render(request, 'properties/my_properties.html', {'properties': properties})


@owner_required
def add_property_view(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.owner = request.user
            prop.save()

            for image_file in request.FILES.getlist('gallery_images'):
                PropertyImage.objects.create(property=prop, image=image_file)

            messages.success(request, f"Property '{prop.title}' added successfully!")
            return redirect('my_properties')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = PropertyForm()

    return render(request, 'properties/property_form.html', {'form': form, 'title': 'Add New Property', 'button_text': 'Publish Property'})


@owner_required
def edit_property_view(request, pk):
    prop = get_object_or_404(Property, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=prop)
        if form.is_valid():
            form.save()

            for image_file in request.FILES.getlist('gallery_images'):
                PropertyImage.objects.create(property=prop, image=image_file)

            messages.success(request, f"Property '{prop.title}' updated successfully!")
            return redirect('my_properties')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = PropertyForm(instance=prop)

    return render(request, 'properties/property_form.html', {
        'form': form,
        'property': prop,
        'title': 'Edit Property',
        'button_text': 'Save Changes',
        'gallery_images': prop.gallery_images.all(),
    })


@owner_required
def delete_property_image_view(request, property_pk, image_pk):
    prop = get_object_or_404(Property, pk=property_pk, owner=request.user)
    gallery_image = get_object_or_404(PropertyImage, pk=image_pk, property=prop)

    if request.method == 'POST':
        gallery_image.delete()
        messages.success(request, "Photo removed from the gallery.")

    return redirect('edit_property', pk=prop.pk)


@owner_required
def delete_property_view(request, pk):
    prop = get_object_or_404(Property, pk=pk, owner=request.user)

    if request.method == 'POST':
        title = prop.title
        prop.delete()
        messages.success(request, f"Property '{title}' has been deleted.")
        return redirect('my_properties')

    return render(request, 'properties/property_confirm_delete.html', {'property': prop})


@owner_required
def incoming_requests_view(request):
    # Get requests for properties owned by this user
    requests_list = RentalRequest.objects.filter(property__owner=request.user).select_related('property', 'tenant', 'tenant__profile')
    return render(request, 'properties/incoming_requests.html', {'requests_list': requests_list})


@owner_required
def accept_request_view(request, pk):
    rental_req = get_object_or_404(RentalRequest, pk=pk, property__owner=request.user)

    if rental_req.status != 'pending':
        messages.warning(request, f"This request is already {rental_req.get_status_display().lower()}.")
        return redirect('incoming_requests')

    if request.method == 'POST':
        rental_req.status = 'accepted'
        rental_req.save()
        messages.success(request, f"You accepted the rental request from {rental_req.tenant.username} for '{rental_req.property.title}'.")
        return redirect('incoming_requests')

    return render(request, 'properties/request_action_confirm.html', {'rental_req': rental_req, 'action': 'accept'})


@owner_required
def reject_request_view(request, pk):
    rental_req = get_object_or_404(RentalRequest, pk=pk, property__owner=request.user)

    if rental_req.status != 'pending':
        messages.warning(request, f"This request is already {rental_req.get_status_display().lower()}.")
        return redirect('incoming_requests')

    if request.method == 'POST':
        rental_req.status = 'rejected'
        rental_req.save()
        messages.info(request, f"You rejected the rental request from {rental_req.tenant.username} for '{rental_req.property.title}'.")
        return redirect('incoming_requests')

    return render(request, 'properties/request_action_confirm.html', {'rental_req': rental_req, 'action': 'reject'})


@owner_required
def owner_dashboard_view(request):
    properties = Property.objects.filter(owner=request.user)
    requests_qs = RentalRequest.objects.filter(property__owner=request.user)

    context = {
        'total_properties': properties.count(),
        'available_properties': properties.filter(is_available=True).count(),
        'total_requests': requests_qs.count(),
        'pending_requests': requests_qs.filter(status='pending').count(),
        'accepted_requests': requests_qs.filter(status='accepted').count(),
        'rejected_requests': requests_qs.filter(status='rejected').count(),
        'recent_properties': properties[:5],
        'recent_requests': requests_qs.select_related('property', 'tenant')[:5],
    }
    return render(request, 'properties/owner_dashboard.html', context)


@tenant_required
def tenant_dashboard_view(request):
    requests_qs = RentalRequest.objects.filter(tenant=request.user)

    context = {
        'total_requests': requests_qs.count(),
        'pending_requests': requests_qs.filter(status='pending').count(),
        'accepted_requests': requests_qs.filter(status='accepted').count(),
        'rejected_requests': requests_qs.filter(status='rejected').count(),
        'cancelled_requests': requests_qs.filter(status='cancelled').count(),
        'recent_requests': requests_qs.select_related('property', 'property__owner')[:5],
    }
    return render(request, 'properties/tenant_dashboard.html', context)
