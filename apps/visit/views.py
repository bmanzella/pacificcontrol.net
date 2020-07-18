from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Visit
from ..user.models import User
from ..user.updater import assign_oper_init
from zhuartcc.decorators import require_logged_in, require_staff


# Serves 'visit.html' file. Saves request from form data on POST
@require_logged_in
def submit_visiting_request(request):
    if request.method == 'POST':
        try:
            post = request.POST
            visiting_request = Visit(
                cid=int(post['cid']),
                rating=post['rating'],
                home_facility=post['home_facility'],
                first_name=post['first_name'],
                last_name=post['last_name'],
                email=post['email'],
                reason=post['reason'],
                submitted=timezone.now(),
            )
            visiting_request.save()
            return redirect('/')
        except:
            return HttpResponse('Something was wrong your request!', status=400)

    return render(request, 'visit.html', {'page_title': 'Visit Houston'})


# Gets all visiting requests from local database and serves 'visitRequests.html' file
@require_staff
def view_visiting_requests(request):
    visiting_requests = Visit.objects.all()
    return render(request, 'visitRequests.html', {
        'page_title': 'Visiting Requests',
        'visiting_requests': visiting_requests
    })


# Creates User object from visiting request with CID specified in POST
@require_staff
@require_POST
def accept_visiting_request(request):
    visiting_request = Visit.objects.get(cid=request.POST['cid'])

    # If user is visiting the ARTCC after being marked inactive
    if User.objects.filter(cid=visiting_request.cid).exists():
        edit_user = User.objects.get(cid=visiting_request.cid)
        if edit_user.status == 2:
            edit_user.status = 1
            edit_user.email = visiting_request.email,
            edit_user.oper_init = assign_oper_init(visiting_request.first_name[0], visiting_request.first_name[0]),
            edit_user.rating = visiting_request.rating,
            edit_user.main_role = 'VC'
            edit_user.assign_initial_cert()
            edit_user.save()
    else:
        new_user = User(
            first_name=visiting_request.first_name.capitalize(),
            last_name=visiting_request.last_name.capitalize(),
            cid=visiting_request.cid,
            email=visiting_request.email,
            oper_init=assign_oper_init(visiting_request.first_name[0], visiting_request.last_name[0]),
            home_facility=visiting_request.home_facility,
            rating=visiting_request.rating,
            main_role='VC',
        )
        new_user.assign_initial_cert()
        new_user.save()

    message = {
        'recipient_name': visiting_request.first_name,
        'text': 'Your visiting request has been accepted.',
        'sender': 'Marcus Miller',
        'sender_role': 'Air Traffic Manager'
    }
    send_mail(
        'Welcome to ZHU!',
        render_to_string('emailTemplate.txt', {'message': message}),
        'no-reply@zhuartcc.org',
        [visiting_request.email],
        html_message=render_to_string('emailTemplate.html', {'message': message}),
    )

    visiting_request.delete()
    return HttpResponse(status=200)


# Deletes visiting request with CID specified in POST
@require_staff
@require_POST
def reject_visiting_request(request):
    visiting_request = Visit.objects.get(cid=request.POST['cid'])

    message = {
        'recipient_name': visiting_request.first_name,
        'text': 'Your visiting request has been rejected for the following reason: ' + request.POST['reason'],
        'sender': 'Marcus Miller',
        'sender_role': 'Air Traffic Manager'
    }
    send_mail(
        'Your ZHU Visting Request...',
        render_to_string('emailTemplate.txt', {'message': message}),
        'no-reply@zhuartcc.org',
        [visiting_request.email],
        html_message=render_to_string('emailTemplate.html', {'message': message}),
    )

    visiting_request.delete()
    return HttpResponse(status=200)
