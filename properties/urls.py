from django.urls import path
from . import views

urlpatterns = [
    # Tenant & Public
    path('properties/', views.property_list_view, name='property_list'),
    path('properties/<int:pk>/', views.property_detail_view, name='property_detail'),
    path('properties/<int:pk>/request/', views.send_request_view, name='send_request'),
    path('requests/my-requests/', views.my_requests_view, name='my_requests'),
    path('requests/<int:pk>/cancel/', views.cancel_request_view, name='cancel_request'),
    path('properties/<int:pk>/review/', views.add_review_view, name='add_review'),
    path('tenant/dashboard/', views.tenant_dashboard_view, name='tenant_dashboard'),

    # Property Owner
    path('owner/dashboard/', views.owner_dashboard_view, name='owner_dashboard'),
    path('owner/properties/', views.my_properties_view, name='my_properties'),
    path('owner/properties/add/', views.add_property_view, name='add_property'),
    path('owner/properties/<int:pk>/edit/', views.edit_property_view, name='edit_property'),
    path('owner/properties/<int:pk>/delete/', views.delete_property_view, name='delete_property'),
    path('owner/properties/<int:property_pk>/images/<int:image_pk>/delete/', views.delete_property_image_view, name='delete_property_image'),
    path('owner/requests/', views.incoming_requests_view, name='incoming_requests'),
    path('owner/requests/<int:pk>/accept/', views.accept_request_view, name='accept_request'),
    path('owner/requests/<int:pk>/reject/', views.reject_request_view, name='reject_request'),
]
