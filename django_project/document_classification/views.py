from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from .forms import tag_selection_form, model_name_selection_form, upload_file_form, sentiments_form
from .models import Documents
from doc_api.apps import sample_predict
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
    docs = Documents.objects.all()
    return render(request, 'document_classification/preview_data.html', {'docs':docs})

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
    if request.method == 'POST':
        form = upload_file_form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('document_classification-preview_data')
    else:
        form = upload_file_form()
    return render(request, 'document_classification/upload_confirmation.html', {'form': form})

def upload_file(request):
    if request.method == 'POST':
        form = upload_file_form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('document_classification-preview_data')
    else:
        form = upload_file_form()
    return render(request, 'document_classification/upload_file.html', {'form': form})

def check_sentiment(request):
    if request.method == 'POST':
        form = sentiments_form(request.POST)
        if form.is_valid():
            form.save()
            sample_pred_text = form.cleaned_data.get('text')
            predictions = sample_predict(sample_pred_text, pad=True)
            messages.success(request, f'model name created for {predictions}!')
            return redirect('document_classification-preview_data')
    else:
        form = sentiments_form()
    return render(request, 'document_classification/sentiments_form.html', {'form': form})   
    

def delete_docs(request, pk):
    if request.method == 'POST':
        doc = Documents.objects.get(pk=pk)
        doc.delete()
    return redirect('document_classification-preview_data')