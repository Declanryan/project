from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import upload_file_form, sentiments_form
from .models import Sentiment_Documents
import boto3
from botocore.config import Config
import time, os, sys
from collections import OrderedDict
import pandas as pd
import stanza
import spacy
import json
from spacy import displacy
from io import StringIO
from pprint import pprint
from .tasks import my_task, sentiment_check_task
from celery import Celery
from celery.result import AsyncResult
from django_project.celery import app

def sentiment_celery_example(request):
    result = my_task.delay(10)
    return render(request, 'document_sentiment/sentiment_celery_example.html', context={'task_id': result.task_id})


def sentiment_import_data_type(request):
    return render(request, 'document_sentiment/sentiment_import_data_type.html')

@login_required
def sentiment_upload_file(request):
    if request.method == 'POST':
        form = upload_file_form(request.POST, request.FILES)
        form.instance.author = request.user
        print (form.instance.author)
        if form.is_valid():
           
            form.save()
            return redirect('document_sentiment-sentiment_preview_data')
    else:
        form = upload_file_form()
    return render(request, 'document_sentiment/sentiment_upload_file.html', {'form': form})

@login_required
def sentiment_preview_data(request):
    docs = Sentiment_Documents.objects.filter(author=request.user.id)
    return render(request, 'document_sentiment/sentiment_preview_data.html', {'docs':docs})

def check_sentiment(request):
    
    if request.method == 'POST':
        form = sentiments_form(request.POST)
        if form.is_valid():
            sample_pred_text = form.cleaned_data.get('text')
            nlp = stanza.Pipeline(lang='en', processors='tokenize,sentiment')
            doc = nlp(sample_pred_text)
            for i, sentence in enumerate(doc.sentences):
                print(i, sentence.sentiment)
                result = sentence.sentiment
            form.sentiment = result
            # form.save() # option to save to database
            if result == 0:
                result_str = "Negative" 
            elif result == 1:
                result_str = "Neutral"
            else:
                result_str = "Positive"
            messages.success(request, f'The detected sentiment is {result_str}!')
            request.session['result'] = result
            request.session['sample_pred_text'] = sample_pred_text
            return redirect('document_sentiment-sentiment_results_page')          
    else:
        form = sentiments_form()
    return render(request, 'document_sentiment/sentiments_form.html', {'form': form})

def append_name(filename, type):
    name, ext = os.path.splitext(filename)# split the filename
    return "{file_name}_{text}".format(file_name=name, text=type)# add extracted to name and .csv extension

@login_required
def check_sentiment_csv(request):
    
    if request.method == 'POST':
        try:
            pk =  request.session['pk']# get the file key
            doc = Sentiment_Documents.objects.get(pk=pk)# get the document ref from the database  
            documentName = str(doc.document)# get the name of the doc 
            appended_doc_name = append_name(documentName, "result.csv")# create new name for result doc 

            result= sentiment_check_task.delay(pk) # send to celery worker

            request.session['result'] = result.id # get the id of the task for retrival from storage

            docs = Sentiment_Documents.objects.filter(author=request.user.id, document__contains=".csv")
            return render(request, 'document_sentiment/sentiment_progress_csv.html', context={'task_id': result.task_id, 'docs':docs})
        except:
            messages.error(request, f'unable to process file')
            docs = Sentiment_Documents.objects.filter(author=request.user.id, document__contains=".csv")
            return render(request, 'document_sentiment/sentiment_preview_data_file.html', {'docs':docs})
    else:
        docs = Sentiment_Documents.objects.filter(author=request.user.id, document__contains=".csv")
        return render(request, 'document_sentiment/sentiment_preview_data_file.html', {'docs':docs})

@login_required
def sentiment_preview_data_file(request):
    docs = Sentiment_Documents.objects.filter(author=request.user.id, document__contains=".csv")
    return render(request, 'document_sentiment/sentiment_preview_data_file.html', {'docs':docs})

def check_file(request, pk, filename):
    name, ext = os.path.splitext(filename)# split the filename

    if ext == '.csv':
        request.session['pk'] = pk        
        doc = Sentiment_Documents.objects.get(pk=pk)# get the document ref from the database
        documentName = str(doc.document)# get the real name of the doc     
        aws_id = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret = os.environ.get('AWS_SECRET_ACCESS_KEY')
        REGION = 'eu-west-1'
        client = boto3.client('s3', region_name = REGION, aws_access_key_id=aws_id,
                aws_secret_access_key=aws_secret)
        bucket_name = "doc-sort-file-upload"
        object_key = documentName
        csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        data = pd.read_csv(StringIO(csv_string))
        content = data.to_dict()
        # pprint(content) # testing
        request.session['content'] = content
        return '.csv'

    elif ext == '.txt':
        request.session['pk'] = pk        
        doc = Sentiment_Documents.objects.get(pk=pk)# get the document ref from the database
        documentName = str(doc.document)# get the real name of the doc     
        aws_id = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret = os.environ.get('AWS_SECRET_ACCESS_KEY')
        REGION = 'eu-west-1'
        client = boto3.client('s3', region_name = REGION, aws_access_key_id=aws_id,
                aws_secret_access_key=aws_secret)
        bucket_name = "doc-sort-file-upload"
        object_key = documentName
        csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
        body = csv_obj['Body']
        content = body.read().decode('utf-8')
        
         #pprint(content) # testing
        request.session['content'] = content
        return '.txt'

    else:
        return '.other'

@login_required
def sentiment_select_doc(request, pk):
    if request.method == 'POST':# check for post request
        doc = Sentiment_Documents.objects.get(pk=pk)# get the document ref from the database
        documentName = str(doc.document)# get the real name of the doc
        ext = check_file(request, pk, documentName)
        if ext == '.other': # check if doc is unsupported format
            messages.error(request, f'Please use an extracted file format such as .txt, .csv or begin extraction process on a new file')
            return redirect('document_sentiment-sentiment_preview_data')
        else:
            return redirect('document_sentiment-sentiment_preview_data_file')
    else:
        messages.error(request, f'unable to process file')
    return render(request, 'document_sentiment-sentiment_preview_data.html')   
    
@login_required
def sentiment_delete_docs(request, pk):
    if request.method == 'POST':
        doc = Sentiment_Documents.objects.get(pk=pk)
        doc.delete()
    return redirect('document_sentiment-sentiment_preview_data')

    
@login_required
def sentiment_results_page(request):
    result_id= request.session['result']# define result
    result = AsyncResult(result_id, app=app)# get the result of the task
    data = result.get()
    json_data = json.loads(data)
    print(json_data)
    if request.method == 'POST':
            return render(request, 'document_sentiment/sentiment_results_page.html', {'json_data':json_data})
    else:
         docs = Sentiment_Documents.objects.filter(author=request.user.id, document__contains=".csv")
    return render(request, 'document_sentiment/sentiment_preview_data_file.html', {'docs':docs})
    

    











#########################################################################
    '''
    # Load English tokenizer, tagger, parser, NER and word vectors
    nlp = spacy.load("en_core_web_md")

    # Process whole documents
    
    doc = nlp(result)
    doc_result = ""
    # Analyze syntax
    print("Noun phrases:", [chunk.text for chunk in doc.noun_chunks])
    print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "VERB"])
'''