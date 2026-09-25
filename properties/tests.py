import datetime
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Profile
from properties.models import Property, RentalRequest


class PropertyOwnerAndTenantTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Property Owner user
        self.owner = User.objects.create_user(
            username='owner1',
            email='owner1@havenhues.com',
            password='OwnerPassword123!',
            first_name='John',
            last_name='Owner'
        )
        self.owner.profile.role = 'owner'
        self.owner.profile.save()

        # Create Another Property Owner user
        self.owner2 = User.objects.create_user(
            username='owner2',
            email='owner2@havenhues.com',
            password='OwnerPassword123!',
            first_name='Second',
            last_name='Owner'
        )
        self.owner2.profile.role = 'owner'
        self.owner2.profile.save()

        # Create Tenant user
        self.tenant = User.objects.create_user(
            username='tenant1',
            email='tenant1@havenhues.com',
            password='TenantPassword123!',
            first_name='Alice',
            last_name='Tenant'
        )
        self.tenant.profile.role = 'tenant'
        self.tenant.profile.save()

        # Create Another Tenant user
        self.tenant2 = User.objects.create_user(
            username='tenant2',
            email='tenant2@havenhues.com',
            password='TenantPassword123!',
            first_name='Bob',
            last_name='Tenant'
        )
        self.tenant2.profile.role = 'tenant'
        self.tenant2.profile.save()

        # Create a sample Property owned by owner1
        self.prop = Property.objects.create(
            owner=self.owner,
            title='Sunset Luxury Apartment',
            description='A beautiful 2-bedroom apartment with ocean view.',
            property_type='apartment',
            price_per_month=2200.00,
            location='Miami, FL',
            bedrooms=2,
            bathrooms=2,
            area_sqft=1100,
            is_available=True
        )

    # --------------------------------------------------------------------------
    # Property Owner Role Tests
    # --------------------------------------------------------------------------

    def test_owner_can_add_property(self):
        self.client.login(username='owner1', password='OwnerPassword123!')
        response = self.client.post(reverse('add_property'), {
            'title': 'Downtown Modern Loft',
            'property_type': 'condo',
            'price_per_month': '1850.00',
            'location': 'Seattle, WA',
            'bedrooms': 1,
            'bathrooms': 1,
            'area_sqft': 800,
            'description': 'Bright loft in the heart of downtown.',
            'is_available': True
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Property.objects.filter(title='Downtown Modern Loft', owner=self.owner).exists())

    def test_owner_can_add_property_with_house_information(self):
        self.client.login(username='owner1', password='OwnerPassword123!')
        response = self.client.post(reverse('add_property'), {
            'title': 'Grand Villa & Garden',
            'property_type': 'villa',
            'price_per_month': '4500.00',
            'location': 'Austin, TX',
            'bedrooms': 4,
            'bathrooms': 3,
            'area_sqft': 3200,
            'description': 'Stunning family villa with private pool and garden.',
            'furnished_status': 'furnished',
            'parking_info': '2 Car Garage + Driveway',
            'pet_friendly': True,
            'year_built': 2022,
            'security_deposit': '4500.00',
            'utilities_included': 'Water, Trash, High-speed Fiber',
            'amenities': 'Private Pool, Smart Thermostat, Wine Cellar, Solar Panels',
            'is_available': True
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        villa = Property.objects.get(title='Grand Villa & Garden')
        self.assertEqual(villa.furnished_status, 'furnished')
        self.assertEqual(villa.parking_info, '2 Car Garage + Driveway')
        self.assertTrue(villa.pet_friendly)
        self.assertEqual(villa.year_built, 2022)
        self.assertEqual(villa.security_deposit, 4500.00)
        self.assertEqual(villa.utilities_included, 'Water, Trash, High-speed Fiber')
        self.assertIn('Private Pool', villa.amenities)

        # Test filtering by pet_friendly and furnished
        filter_res = self.client.get(reverse('property_list'), {'pet_friendly': 'on', 'furnished_status': 'furnished'})
        self.assertEqual(filter_res.status_code, 200)
        self.assertContains(filter_res, 'Grand Villa &amp; Garden')

    def test_tenant_cannot_add_property(self):
        self.client.login(username='tenant1', password='TenantPassword123!')
        response = self.client.get(reverse('add_property'), follow=True)
        # Should be restricted and redirected
        self.assertContains(response, 'Access restricted: This area is only available to Property Owner accounts.')
        self.assertFalse(response.redirect_chain == [])

    def test_owner_can_edit_their_own_property(self):
        self.client.login(username='owner1', password='OwnerPassword123!')
        response = self.client.post(reverse('edit_property', args=[self.prop.pk]), {
            'title': 'Sunset Luxury Apartment - Updated',
            'property_type': 'apartment',
            'price_per_month': '2350.00',
            'location': 'Miami, FL',
            'bedrooms': 2,
            'bathrooms': 2,
            'area_sqft': 1100,
            'description': 'Updated ocean view apartment.',
            'is_available': True
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.prop.refresh_from_db()
        self.assertEqual(self.prop.title, 'Sunset Luxury Apartment - Updated')
        self.assertEqual(self.prop.price_per_month, 2350.00)

    def test_owner_cannot_edit_another_owner_property(self):
        self.client.login(username='owner2', password='OwnerPassword123!')
        response = self.client.get(reverse('edit_property', args=[self.prop.pk]))
        self.assertEqual(response.status_code, 404)

    def test_owner_can_delete_their_own_property(self):
        self.client.login(username='owner1', password='OwnerPassword123!')
        response = self.client.post(reverse('delete_property', args=[self.prop.pk]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Property.objects.filter(pk=self.prop.pk).exists())

    def test_owner_cannot_delete_another_owner_property(self):
        self.client.login(username='owner2', password='OwnerPassword123!')
        response = self.client.post(reverse('delete_property', args=[self.prop.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Property.objects.filter(pk=self.prop.pk).exists())

    def test_tenant_cannot_edit_property(self):
        self.client.login(username='tenant1', password='TenantPassword123!')
        response = self.client.post(reverse('edit_property', args=[self.prop.pk]), {
            'title': 'Hacked Title',
            'property_type': 'apartment',
            'price_per_month': '500.00',
            'location': 'Miami, FL',
            'bedrooms': 2,
            'bathrooms': 2,
            'description': 'Attempted change',
            'is_available': True
        }, follow=True)
        self.assertContains(response, 'Access restricted: This area is only available to Property Owner accounts.')
        self.prop.refresh_from_db()
        self.assertEqual(self.prop.title, 'Sunset Luxury Apartment')

    def test_tenant_cannot_delete_property(self):
        self.client.login(username='tenant1', password='TenantPassword123!')
        response = self.client.post(reverse('delete_property', args=[self.prop.pk]), follow=True)
        self.assertContains(response, 'Access restricted: This area is only available to Property Owner accounts.')
        self.assertTrue(Property.objects.filter(pk=self.prop.pk).exists())

    def test_owner_view_incoming_rental_requests(self):
        # Create a rental request from tenant1 for owner's property
        req = RentalRequest.objects.create(
            property=self.prop,
            tenant=self.tenant,
            move_in_date=datetime.date.today() + datetime.timedelta(days=15),
            lease_duration_months=12,
            message='Hello, I love this apartment and want to move in soon.',
            status='pending'
        )

        self.client.login(username='owner1', password='OwnerPassword123!')
        response = self.client.get(reverse('incoming_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sunset Luxury Apartment')
        self.assertContains(response, 'Alice')
        self.assertContains(response, 'tenant1')

    def test_owner_can_accept_and_reject_rental_request(self):
        req = RentalRequest.objects.create(
            property=self.prop,
            tenant=self.tenant,
            move_in_date=datetime.date.today() + datetime.timedelta(days=15),
            lease_duration_months=12,
            message='Interested in lease.',
            status='pending'
        )

        self.client.login(username='owner1', password='OwnerPassword123!')

        # Accept request
        response_accept = self.client.post(reverse('accept_request', args=[req.pk]), follow=True)
        self.assertEqual(response_accept.status_code, 200)
        req.refresh_from_db()
        self.assertEqual(req.status, 'accepted')

        # Reset to pending and reject
        req.status = 'pending'
        req.save()

        response_reject = self.client.post(reverse('reject_request', args=[req.pk]), follow=True)
        self.assertEqual(response_reject.status_code, 200)
        req.refresh_from_db()
        self.assertEqual(req.status, 'rejected')

    # --------------------------------------------------------------------------
    # Tenant Role Tests
    # --------------------------------------------------------------------------

    def test_tenant_can_browse_properties(self):
        response = self.client.get(reverse('property_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sunset Luxury Apartment')
        self.assertContains(response, 'Miami, FL')

    def test_tenant_can_view_property_details(self):
        response = self.client.get(reverse('property_detail', args=[self.prop.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sunset Luxury Apartment')
        self.assertContains(response, '$2200.00')

    def test_tenant_can_send_rental_request(self):
        self.client.login(username='tenant1', password='TenantPassword123!')
        move_date = (datetime.date.today() + datetime.timedelta(days=10)).isoformat()
        response = self.client.post(reverse('send_request', args=[self.prop.pk]), {
            'move_in_date': move_date,
            'lease_duration_months': 12,
            'message': 'Looking forward to moving into this place!'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(RentalRequest.objects.filter(property=self.prop, tenant=self.tenant, status='pending').exists())

    def test_owner_cannot_send_rental_request(self):
        self.client.login(username='owner1', password='OwnerPassword123!')
        response = self.client.get(reverse('send_request', args=[self.prop.pk]), follow=True)
        self.assertContains(response, 'Access restricted: This action is intended for Tenant accounts.')

    def test_tenant_can_view_their_requests(self):
        req = RentalRequest.objects.create(
            property=self.prop,
            tenant=self.tenant,
            move_in_date=datetime.date.today() + datetime.timedelta(days=10),
            lease_duration_months=6,
            message='Short-term lease request.',
            status='pending'
        )

        self.client.login(username='tenant1', password='TenantPassword123!')
        response = self.client.get(reverse('my_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sunset Luxury Apartment')
        self.assertContains(response, 'Pending')

    def test_tenant_can_cancel_pending_request(self):
        req = RentalRequest.objects.create(
            property=self.prop,
            tenant=self.tenant,
            move_in_date=datetime.date.today() + datetime.timedelta(days=10),
            lease_duration_months=6,
            message='Please cancel if not available.',
            status='pending'
        )

        self.client.login(username='tenant1', password='TenantPassword123!')
        response = self.client.post(reverse('cancel_request', args=[req.pk]), follow=True)
        self.assertEqual(response.status_code, 200)
        req.refresh_from_db()
        self.assertEqual(req.status, 'cancelled')
        self.assertContains(response, 'has been cancelled')

    def test_tenant_cannot_cancel_already_accepted_request(self):
        req = RentalRequest.objects.create(
            property=self.prop,
            tenant=self.tenant,
            move_in_date=datetime.date.today() + datetime.timedelta(days=10),
            lease_duration_months=12,
            message='Approved request',
            status='accepted'
        )

        self.client.login(username='tenant1', password='TenantPassword123!')
        response = self.client.post(reverse('cancel_request', args=[req.pk]), follow=True)
        self.assertEqual(response.status_code, 200)
        req.refresh_from_db()
        self.assertEqual(req.status, 'accepted')
        self.assertContains(response, 'You can only cancel pending requests')

    def test_tenant_cannot_cancel_another_tenant_request(self):
        req = RentalRequest.objects.create(
            property=self.prop,
            tenant=self.tenant,
            move_in_date=datetime.date.today() + datetime.timedelta(days=10),
            lease_duration_months=12,
            message='Tenant 1 request',
            status='pending'
        )

        self.client.login(username='tenant2', password='TenantPassword123!')
        response = self.client.get(reverse('cancel_request', args=[req.pk]))
        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_user_cannot_send_request(self):
        response = self.client.get(reverse('send_request', args=[self.prop.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_tenant_cannot_send_duplicate_pending_request(self):
        self.client.login(username='tenant1', password='TenantPassword123!')
        move_date = (datetime.date.today() + datetime.timedelta(days=10)).isoformat()
        # First request
        self.client.post(reverse('send_request', args=[self.prop.pk]), {
            'move_in_date': move_date,
            'lease_duration_months': 12,
            'message': 'First application'
        })
        # Attempt second request
        response = self.client.get(reverse('send_request', args=[self.prop.pk]), follow=True)
        self.assertContains(response, 'You already have a Pending request for this property.')
        self.assertEqual(RentalRequest.objects.filter(property=self.prop, tenant=self.tenant).count(), 1)

    def test_tenant_cannot_send_request_for_unavailable_property(self):
        self.prop.is_available = False
        self.prop.save()

        self.client.login(username='tenant1', password='TenantPassword123!')
        response = self.client.get(reverse('send_request', args=[self.prop.pk]), follow=True)
        self.assertContains(response, 'This property is currently not available for rent.')

    def test_non_owner_cannot_accept_or_reject_request(self):
        req = RentalRequest.objects.create(
            property=self.prop,
            tenant=self.tenant,
            move_in_date=datetime.date.today() + datetime.timedelta(days=10),
            lease_duration_months=12,
            message='Application',
            status='pending'
        )

        # Other owner tries to accept
        self.client.login(username='owner2', password='OwnerPassword123!')
        response_accept = self.client.post(reverse('accept_request', args=[req.pk]))
        self.assertEqual(response_accept.status_code, 404)

        # Tenant tries to accept
        self.client.login(username='tenant1', password='TenantPassword123!')
        response_tenant_accept = self.client.post(reverse('accept_request', args=[req.pk]), follow=True)
        self.assertContains(response_tenant_accept, 'Access restricted: This area is only available to Property Owner accounts.')
