from django.contrib.auth.models import User
from rest_framework import status
from hiway.core.test import base
from django.utils import timezone
from .models import FoodSubscription
from hiway import settings
from datetime import timedelta
import mock
from django.core.exceptions import ValidationError


class CategoryTests(base.HiwayIntegrationTests):
    
    def setUp(self):
        self.user = User.objects.create_superuser(username="testcase", email="test@test.com", password="testcase")
        self.user1 = User.objects.create_superuser(username="test", email="test@test.com", password="test")
        self.user.save()
        self.user1.save()
        self.user2, self.user3 = self.create_user('user2', 'user3')
        self.login(self.user)
        day = timezone.now().date() + timedelta(days=4)
        self.food_subscription_obj_1 = FoodSubscription.objects.create(user=self.user, date=day, is_eating="Yes")
        self.food_subscription_obj_2 = FoodSubscription.objects.create(user=self.user, date=timezone.now().date() + timedelta(days=1), is_eating="No")
        self.food_subscription_obj_3 = FoodSubscription.objects.create(user=self.user, date=timezone.now().date() + timedelta(days=2), is_eating="No")
    
    def test_post(self):
        """Test case for post"""
        self.client.login(username="testcase", password="testcase")
        url = '/api/v1/dinner-attendance/'
        day = timezone.now().date() + timedelta(days=2)
        data = {"user":self.user.id, "date":day, "is_eating" : "Yes"}
        data = self.request_post_data(self.user, url, data, 201)
        food_subscription = FoodSubscription.objects.get(id=data["id"])
        self.assertEquals(day,food_subscription.date)       
                      
    def test_get(self):
        """Test case for get request.Test data is created at the setup function"""
        self.client.login(username="testcase", password="testcase")
        url = '/api/v1/dinner-attendance/?from=' + str(timezone.now().date()) + '&to=' + str(timezone.now().date() + timedelta(days=3))
        data = self.request_get_data(self.user, url)
        self.assertEquals(2,data["count"])
 
             
    def test_post_authentication(self):
        """Test case for checking one user cannot fill or update the other user form"""
        self.client.login(username="testcase", password="testcase")
        url = '/api/v1/dinner-attendance/'
        day = timezone.now().date() + timedelta(days=2)    
        data = {"user":self.user1.id, "date":day, "is_eating" : "Yes"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
         
    def test_post_today_after_3PM(self):
        '''Test case - If a user is trying to modify the decission after 3 PM'''
        self.client.login(username="testcase", password="testcase")
        url = '/api/v1/dinner-attendance/'
        day = timezone.now().date()
        data = {"user":self.user.id, "date":day, "is_eating" : "Yes"}
        freeze_time = settings.DEFAULT_DINNER_FREEZE_TIME
        with mock.patch('django.utils.timezone', return_value = 9) as current_time :
            if (current_time > freeze_time.hour):
                try:
                    self.client.post(url, data)
                    self.fail("Testcase failed.")
                except ValidationError as exception:
                    self.assertEqual(exception[0], "Invalid time")
        
    def test_post_previous_day(self):
        '''Test case - If a user is trying to modify the decission for the previous days.'''
        self.client.login(username="testcase", password="testcase")
        url = '/api/v1/dinner-attendance/'
        day = timezone.now().date() - timedelta(days=2)
        data = {"user":self.user.id, "date":day, "is_eating" : "Yes"}
        try:
            self.client.post(url, data)
            self.fail("Testcase failed.")
        except ValidationError as exception:
            self.assertEqual(exception[0], "Invalid time")
               
    def test_update(self):
        """Test case for update an entry(Put)"""
        self.client.login(username="testcase", password="testcase")
        entry_id = str(self.food_subscription_obj_1.id)
        url = '/api/v1/dinner-attendance/' + entry_id +'/'
        day = timezone.now().date() + timedelta(days=4)
        data = {"user":self.user.id, "date":day, "is_eating" : "No"}
        data = self.request_put_data(self.user, url, data)
        self.assertEquals('False',str(data['is_eating']))
