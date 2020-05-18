from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User



def home(request):
    
    return render(request, 'document_classification/home.html')

def choose_model(request):
    
    return render(request, 'document_classification/choose_model.html')

def import_data_type(request):
    
    return render(request, 'document_classification/import_data_type.html')

def model_name(request):
    
    return render(request, 'document_classification/model_name.html')

def preview_data(request):
    
    return render(request, 'document_classification/preview_data.html')

def results_page(request):
    
    return render(request, 'document_classification/reults_page.html')

def setup_complete(request):
    
    return render(request, 'document_classification/setup_complete.html')

def tag_selection(request):
    
    return render(request, 'document_classification/tag_selection.html')

def testing(request):
    
    return render(request, 'document_classification/testing.html')
def home(request):
    
    return render(request, 'document_classification/home.html')

def upload_confirmation(request):
    
    return render(request, 'document_classification/upload_confirmation.html')

def upload_file(request):
    
    return render(request, 'document_classification/upload_file.html')

