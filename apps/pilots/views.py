from itertools import groupby

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from apps.administration.models import ActionLog
from apps.pilots.models import Scenery
from apps.user.models import User
from zhuartcc.decorators import require_staff


def view_artcc_map(request):
    return render(request, 'artcc_map.html', {'page_title': 'ARTCC Map'})


def view_scenery(request):
    sceneries = Scenery.objects.all().order_by('simulator')
    scenery_sorted = {k: list(g) for k, g in groupby(sceneries, key=lambda scenery: scenery.get_simulator_display())}
    simulators = Scenery._meta.get_field('simulator').choices
    return render(request, 'scenery.html', {
        'page_title': 'Scenery',
        'sceneries': scenery_sorted,
        'simulators': simulators
    })


@require_staff
@require_POST
def edit_scenery(request):
    try:
        scenery = Scenery.objects.get(id=request.POST['id'])
        scenery.name = request.POST['name']
        scenery.simulator = request.POST['simulator']
        scenery.link = request.POST['link']
        scenery.payware = True if 'payware' in request.POST else False
        scenery.save()

        user = User.objects.get(cid=request.session['cid'])
        ActionLog(action=f'Scenery "{scenery.name}" modified by {user.full_name}.').save()

        return HttpResponse(status=200)
    except:
        return HttpResponse('Something was wrong your request!', status=400)


@require_staff
@require_POST
def add_scenery(request):
    try:
        scenery = Scenery(
            name=request.POST['name'],
            simulator=request.POST['simulator'],
            link=request.POST['link'],
            payware=True if 'payware' in request.POST else False
        )
        scenery.save()

        user = User.objects.get(cid=request.session['cid'])
        ActionLog(action=f'Scenery "{scenery.name}" created by {user.full_name}.').save()

        return HttpResponse(status=200)
    except:
        return HttpResponse('Something was wrong your request!', status=400)


@require_staff
@require_POST
def delete_scenery(request):
    try:
        scenery = Scenery.objects.get(id=request.POST['id'])

        user = User.objects.get(cid=request.session['cid'])
        ActionLog(action=f'Scenery "{scenery.name}" deleted by {user.full_name}.').save()

        scenery.delete()

        return HttpResponse(status=200)
    except:
        return HttpResponse('Something was wrong your request!', status=400)
