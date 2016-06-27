from hiway.food_subscription.models import FoodSubscription
from hiway.settings import HIWAY_NOREPLY_MAIL_ID,OPERATIONS_MAIL_ID
from django.template.loader import render_to_string
from celery.app import shared_task
from hiway.metrics import api
from django.utils import timezone

def dinner_attendence_list():
    entries = FoodSubscription.objects.select_related("user").filter(date = timezone.now().date() ,is_eating = True).order_by('user__username')
    return  [{
   "user": entry.user.username,
           } for entry in entries]

def dinner_attendence_list_to_html(today_list, count,date):
    """converting the list to dictionary and rendering it to html page"""
    context = dict(people_eating_dinner=today_list,count=count , date=date)
    return render_to_string('food_subscription/dinner_eating_email.html', context)

@shared_task()
def send_mail_dinner_attendance_count():
    """ send mail to deepak daily about dinner attendance count"""
    people_eating_dinner = dinner_attendence_list() 
    entries = FoodSubscription.objects.select_related().filter(date = timezone.now().date() ,is_eating = True)
    count = len(entries)
    date = timezone.now().date()
    subject = "{count} People Having Dinner Today - {date}".format(count=len(entries),date=timezone.now().date())
    email_string = dinner_attendence_list_to_html(people_eating_dinner, count,date)
    from_address = HIWAY_NOREPLY_MAIL_ID
    to_address = [OPERATIONS_MAIL_ID,]
    api.send_mail(subject, email_string, from_address, to_address, [], [])
