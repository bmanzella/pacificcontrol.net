import os
import ast
import pytz
import requests
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from zhuartcc.overrides import send_mail

from django.template.loader import render_to_string
from django.utils import timezone

from .views import return_inactive_users
from .models import Controller, ControllerSession
from ..user.models import User


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(pull_controllers, 'interval', minutes=1)
    scheduler.add_job(warn_inactive_users, 'cron', day=23)
    scheduler.start()


def pull_controllers():
    airports = ast.literal_eval(os.getenv('AIRPORT_IATA'))
    data = requests.get('https://data.vatsim.net/v3/vatsim-data.json').json()

    for controller in Controller.objects.all():
        if next((entry for entry in data.get('controllers') if entry.get('callsign') == controller.callsign), None):
            controller.last_update = timezone.now()
            controller.save()
        else:
            controller.convert_to_session()
            controller.delete()

    for controller in data.get('controllers'):
        user = User.objects.filter(cid=controller.get('cid')).first()
        if user:
            if controller.get('callsign').split('_')[0] in airports:
                if 0 < controller.get('facility') < 7:
                    if not Controller.objects.filter(callsign=controller.get('callsign')).exists():
                        Controller(
                            user=user,
                            callsign=controller.get('callsign'),
                            frequency=controller.get('frequency'),
                            online_since=pytz.utc.localize(datetime.strptime(controller.get('logon_time'), '%Y-%m-%dT%H:%M:%S%fZ')),
                            last_update=timezone.now(),
                        ).save()


def warn_inactive_users():
    for aggregate in return_inactive_users():
        context = {
            'user': aggregate['user_obj'],
            'hours': round(aggregate['hours']['current'].total_seconds() / 3600, 1),
        }
        send_mail(
            'Controller Activity Warning',
            render_to_string('emails/activity_warning.html', context),
            os.getenv('NO_REPLY'),
            [aggregate['user_obj'].email],
            fail_silently=True,
        )
