from django.shortcuts import render

def landing(request):
    context = {}
    return render(request, "landing.html", context)