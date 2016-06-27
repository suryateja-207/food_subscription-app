from django.contrib import admin
from hiway.food_subscription import models


class FoodSubscriptionAdmin(admin.ModelAdmin):
     list_display = ('user','date','is_eating')
     list_filter = ('user','is_eating','date')
     
admin.site.register(models.FoodSubscription, FoodSubscriptionAdmin)