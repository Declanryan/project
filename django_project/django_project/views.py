from django.shortcuts import render



def home(request): 
    return render(request, 'django_project/home.html')

def price_plan(request): 
    return render(request, 'django_project/price_plans.html')

def choose_model(request):
    return render(request, 'django_project/choose_model.html')

def about(request):
    return render(request, 'django_project/about.html', {'title': 'About'})