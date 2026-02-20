# Landing page view - the home page of the site
from django.shortcuts import render

def home(request):
    return render(request, 'core/home.html')


