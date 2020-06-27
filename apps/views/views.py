from django.shortcuts import render


def view_homepage(request):
    return render(request, 'homepage.html')


def view_privacy_policy(request):
    return render(request, 'privacy.html')


def view_admin_panel(request):
    return render(request, 'admin.html')
