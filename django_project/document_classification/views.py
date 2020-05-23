from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from .forms import tag_selection_form, model_name_selection_form


def home(request): 
    return render(request, 'document_classification/home.html')

def choose_model(request):
    return render(request, 'document_classification/choose_model.html')

def import_data_type(request):
    return render(request, 'document_classification/import_data_type.html')

def model_name(request):
    if request.method == 'POST':
        form = model_name_selection_form(request.POST)
        if form.is_valid():
            # form.save()
            model_name = form.cleaned_data.get('username')
            messages.success(request, f'model name created for {model_name}!')
            return redirect('document_classification/setup_complete.html')
    else:
        form = model_name_selection_form()
        return render(request, 'document_classification/model_name.html', {'form': form})

def preview_data(request):
    return render(request, 'document_classification/preview_data.html')

def results_page(request):
    return render(request, 'document_classification/results_page.html')

def setup_complete(request):
    return render(request, 'document_classification/setup_complete.html')

def tag_selection(request):
    if request.method == 'POST':
        form = tag_selection_form(request.POST)
        if form.is_valid():
            # form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'tag_selection created for {username}!')
            return redirect('document_classification/model_name.html')
    else:
        form = tag_selection_form()
        return render(request, 'document_classification/tag_selection.html', {'form': form})

def testing(request): 
    return render(request, 'document_classification/testing.html')

def home(request): 
    return render(request, 'document_classification/home.html')

def upload_confirmation(request):
    return render(request, 'document_classification/upload_confirmation.html')

def upload_file(request):
    return render(request, 'document_classification/upload_file.html')

