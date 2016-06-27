from hiway.food_subscription.models import FoodSubscription
from rest_framework.response import Response
from rest_framework import status
from hiway.api import permissions
from rest_framework import viewsets
from django.db.models import Q
from rest_framework import serializers
from django.utils import timezone
from hiway.settings import DEFAULT_DINNER_FREEZE_TIME
from datetime import datetime
from django.core.exceptions import ValidationError


class FoodSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer to serialize the object."""
    class Meta:
        model = FoodSubscription
        fields = ("user", "date", "is_eating", "id")
        
        
class FoodSubscriptionView(viewsets.ModelViewSet):
    '''view for get and post'''
    serializer_class = FoodSubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated, permissions.IsOwnerOrReadOnly)
    queryset = FoodSubscription.objects.all()
    
    def get_queryset(self):
        '''It will get all the details previously filled by the user. '''
        if(self.request.query_params.get('from') or self.request.query_params.get('to')):    
            min_date = self.request.query_params.get('from', timezone.now().date())
            max_date = self.request.query_params.get('to', timezone.now().date())
            entries = self.queryset.filter(Q(user = self.request.user.id),Q(date__range=[min_date, max_date]))
        else :
            entries = self.queryset.filter(Q(user = self.request.user.id))
        return entries
    
    def create(self, request, *args, **kwargs):
        '''Posting the data from form to database.'''
        serializer = FoodSubscriptionSerializer(data=request.data)
        data = request.data
        if (self.is_authorised(data)):
            return Response('Not Allowed', status=status.HTTP_403_FORBIDDEN) 
        if serializer.is_valid():
            if self.is_invalid_time(data):
                raise ValidationError("Invalid time")
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        '''Updating the entry if there is any on the same date.'''
        data = request.data
        if (self.is_authorised(data)):
            return Response('Not Allowed', status=status.HTTP_403_FORBIDDEN)
        elif self.is_invalid_time(data):
            raise ValidationError("Invalid time")
        else:
            return super(FoodSubscriptionView, self).update(request)        
                
    def is_authorised(self,data):
        '''Checking for the user authorization.'''
        if int(data['user']) != int(self.request.user.id) :
            return True
        else :
            return False
        
    def is_invalid_time(self,data):
        """Checking the date and time user is posting .If it is greater than 3 on same day it will not post in the database.
         and if the date is past day also it will not post in database."""
        freeze_time = DEFAULT_DINNER_FREEZE_TIME
        today = timezone.now().date()
        date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        if ((date  == today  and timezone.now().time() > freeze_time.time())) \
            or date < today :
            return True
        else :
            return False
