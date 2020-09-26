from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import upload_file_form, sentiments_form
from .models import Sentiment_Documents
from .apps import DocumentSentimentConfig
import boto3
from botocore.config import Config
import time
# Create your views here.

def import_data_type(request):
    return render(request, 'document_sentiment/import_data_type.html')

def upload_confirmation(request):
    if request.method == 'POST':
        form = upload_file_form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('document_sentiment-preview_data')
    else:
        form = upload_file_form()
    return render(request, 'document_sentiment/upload_confirmation.html', {'form': form})

def upload_file(request):
    if request.method == 'POST':
        form = upload_file_form(request.POST, request.FILES)
        form.instance.author = request.user
        if form.is_valid():
           
            form.save()
            return redirect('document_sentiment-preview_data')
    else:
        form = upload_file_form()
    return render(request, 'document_sentiment/upload_file.html', {'form': form})

def preview_data(request):
    docs = Sentiment_Documents.objects.filter(author=request.user)
    return render(request, 'document_sentiment/preview_data.html', {'docs':docs})

def check_sentiment(request):
    if request.method == 'POST':
        form = sentiments_form(request.POST)
        if form.is_valid():
            sample_pred_text = form.cleaned_data.get('text')
            predictions = DocumentSentimentConfig.sample_predict(sample_pred_text, pad=True)
            form.sentiment = predictions
            form.save()
            messages.success(request, f'The detected sentiment is {predictions}!')
            
    else:
        form = sentiments_form()
    return render(request, 'document_sentiment/sentiments_form.html', {'form': form})   
    

def delete_docs(request, pk):
    if request.method == 'POST':
        doc = Sentiment_Documents.objects.get(pk=pk)
        doc.delete()
    return redirect('document_sentiment-preview_data')

def results_page(request):
    return render(request, 'document_sentiment/results_page.html')