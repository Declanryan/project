from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import tag_selection_form, model_name_selection_form, upload_file_form
from .models import Classification_Documents
import boto3, botocore
from botocore.config import Config
import time, os, sys
from tempfile import NamedTemporaryFile
from smart_open import open
from collections import defaultdict
from io import StringIO
import numpy as np
import pandas as pd
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
from gensim.test.utils import datapath
import spacy
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en.stop_words import STOP_WORDS
from tqdm import tqdm as tqdm
from pprint import pprint
import json

def home(request): 
    return render(request, 'document_classification/home.html')

def price_plan(request): 
    return render(request, 'document_classification/price_plans.html')

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
    docs = Classification_Documents.objects.filter(author=request.user.id)
    return render(request, 'document_classification/preview_data.html', {'docs':docs})

def extract_preview_file(request):
    docs = Classification_Documents.objects.filter(author=request.user.id)
    return render(request, 'document_classification/extract_preview_file.html', {'docs':docs})

def csv_preview_file(request):
    docs = Classification_Documents.objects.filter(author=request.user.id)
    return render(request, 'document_classification/csv_preview_file.html', {'docs':docs})

def json_preview_file(request):
    docs = Classification_Documents.objects.filter(author=request.user.id)
    return render(request, 'document_classification/json_preview_file.html', {'docs':docs})

def results_page(request):
    return render(request, 'document_classification/results_page.html')

def setup_complete(request):
    return render(request, 'document_classification/setup_complete.html')

def tag_selection(request):
    if request.method == 'POST':
        labels_list =[]
        form = tag_selection_form(request.POST)
        if form.is_valid():
            labels_list.extend('Tag0, Tag1, Tag2, Tag3, Tag4, Tag5, Tag6, Tag7, Tag8, Tag9')
            return redirect('document_classification-results_page')
    else:
        form = tag_selection_form()
        return render(request, 'document_classification/tag_selection.html', {'form': form})

def testing(request): 
    return render(request, 'document_classification/testing.html')


def json_upload_file(request):
    if request.method == 'POST':
        form = upload_file_form(request.POST, request.FILES)
        form.instance.author = request.user
        if form.is_valid():
            form.save()
            return redirect('document_classification-json_preview_file')
    else:
        form = upload_file_form()
    return render(request, 'document_classification/json_upload_file.html', {'form': form})

def extract_upload_file(request):
    if request.method == 'POST':
        form = upload_file_form(request.POST, request.FILES)
        form.instance.author = request.user
        if form.is_valid():
            form.save()
            return redirect('document_classification-extract_preview_file')
    else:
        form = upload_file_form()
    return render(request, 'document_classification/extract_upload_file.html', {'form': form})

def csv_upload_file(request):
    if request.method == 'POST':
        form = upload_file_form(request.POST, request.FILES)
        form.instance.author = request.user
        if form.is_valid():
            form.save()
            return redirect('document_classification-csv_preview_file')
    else:
        form = upload_file_form()
    return render(request, 'document_classification/csv_upload_file.html', {'form': form})



def upload_confirmation(request):
    if request.method == 'POST':
        form = upload_file_form(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('document_classification-preview_data')
    else:
        form = upload_file_form()
    return render(request, 'document_classification/upload_confirmation.html', {'form': form})

def delete_docs(request, pk):
    if request.method == 'POST':
        doc = Classification_Documents.objects.get(pk=pk)
        doc.delete()
    return redirect('document_classification-preview_data')

def append_name(filename, type):
    name, ext = os.path.splitext(filename)# split the filename
    return "{file_name}_{text}{ext}".format(file_name=name, text=type, ext=".txt")# add extracted to name and .txt extension

def check_extension(filename):
    name, ext = os.path.splitext(filename)# split the filename
    if ext == '.pdf':
        return '.pdf'
    else:
        return '.other'

def check_file(request, pk, filename):
    name, ext = os.path.splitext(filename)# split the filename

    if ext == '.csv':
        request.session['pk'] = pk        
        doc = Classification_Documents.objects.get(pk=pk)# get the document ref from the database
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
        content = data.head().to_dict()
        pprint(content)
        request.session['content'] = content
        return '.csv'

    elif ext == '.txt':
        request.session['pk'] = pk        
        doc = Classification_Documents.objects.get(pk=pk)# get the document ref from the database
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
        # content = file.read().replace("\n", " ")
        pprint(content)
        request.session['content'] = content
        return '.txt'

    else:
        return '.other'


def select_doc(request, pk):
    if request.method == 'POST':# check for post request
        doc = Classification_Documents.objects.get(pk=pk)# get the document ref from the database
        documentName = str(doc.document)# get the real name of the doc
        ext = check_file(request, pk, documentName)
        if ext == '.other': # check if doc is unsupported format
            messages.error(request, f'Please use an extracted file format such as .txt, .csv or begin extraction process on a new file')
            return redirect('document_classification-extract_preview_file')
        else:
            return redirect('document_classification-display_extracted_text')
    else:
        messages.error(request, f'unable to process file')
    return render(request, 'document_classification-extract_preview_file.html')
    

def extract_doc(request, pk):
    if request.method == 'POST':# check for post request
        doc = Classification_Documents.objects.get(pk=pk)# get the document ref from the database
        documentName = str(doc.document)# get the real name of the doc
        ext = check_file(documentName)
        if ext == '.pdf': # check if doc is a pdf
            extract_doc_name = append_name(documentName, "extracted")# create new name for extracted doc
            content = extract_pdf_docs(request, pk)
            request.session['content'] = content
            s3 = boto3.resource('s3')        
            s3.Object('doc-sort-file-upload', extract_doc_name).put(Body=content)
            extraxt_doc = Classification_Documents(username=request.user, description='extracted text', document=extract_doc_name, author=request.user)
            extraxt_doc.save()
            return redirect('document_classification-display_extracted_text')
        else:
            extract_doc_name = append_name(documentName, "extracted")# create new name for extracted doc
            content = "" 
            my_config = Config(# configuration of client for s3 retrieval
            region_name = 'eu-west-1', signature_version = 'v4',
            retries = {'max_attempts': 10, 'mode': 'standard'})
            textract = boto3.client('textract', config=my_config)# initiate client
            response = textract.detect_document_text(Document={
            'S3Object': {'Bucket': "doc-sort-file-upload",'Name': documentName}})# retrieve doc from s3 and pass to textract for extraction
            for item in response["Blocks"]:# iterate trough json response
                if item["BlockType"] == "LINE":
                    content += (item["Text"])
                    # print ('\033[94m' +  item["Text"] + '\033[0m') # TESTING
            
            s3 = boto3.resource('s3')        
            s3.Object('doc-sort-file-upload', extract_doc_name).put(Body=content)
            extraxt_doc = Classification_Documents(username=request.user, description='extracted text', document=extract_doc_name, author=request.user)
            extraxt_doc.save()
            request.session['content'] = content
            return redirect('document_classification-display_extracted_text')
    else:
        messages.error(request, f'unable to extract text!')
    return render(request, 'document_classification-extract_preview_file.html')


def display_extracted_text(request):
    docs = Classification_Documents.objects.filter(author=request.user.id, document__contains="extracted")
    return render(request, 'document_classification/display_extracted_text.html', {'docs':docs})

def display_csv_text(request):
    docs = Classification_Documents.objects.filter(author=request.user.id, document__contains="csv")
    return render(request, 'document_classification/display_csv_text.html', {'docs':docs})

def display_json_text(request):
    docs = Classification_Documents.objects.filter(author=request.user.id, document__contains="json")
    return render(request, 'document_classification/display_extracted_json.html', {'docs':docs})

def topic_extraction(request):
    # if request.method == 'POST':# check for post request
    pk = request.session['pk']
    doc = Classification_Documents.objects.get(pk=pk)# get the document ref from the database
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
    '''
    
    newest_doc = data['content']

    nlp = spacy.load("en_core_web_md")

    # My list of stop words.
    stop_list = ["Mrs.","Ms.","say","WASHINGTON","'s","Mr.",]

    # Updates spaCy's default stop words list with my additional words. 
    nlp.Defaults.stop_words.update(stop_list)

    # Iterates over the words in the stop words list and resets the "is_stop" flag.
    for word in STOP_WORDS:
        lexeme = nlp.vocab[word]
        lexeme.is_stop = True

    def lemmatizer(doc):
        # This takes in a doc of tokens from the NER and lemmatizes them. 
        # Pronouns (like "I" and "you" get lemmatized to '-PRON-', so I'm removing those.
        doc = [token.lemma_ for token in doc if token.lemma_ != '-PRON-']
        doc = u' '.join(doc)
        return nlp.make_doc(doc)
        
    def remove_stopwords(doc):
        # This will remove stopwords and punctuation.
        # Use token.text to return strings, which we'll need for Gensim.
        doc = [token.text for token in doc if token.is_stop != True and token.is_punct != True]
        return doc

    # The add_pipe function appends our functions to the default pipeline.
    nlp.add_pipe(lemmatizer,name='lemmatizer',after='ner')
    nlp.add_pipe(remove_stopwords, name="stopwords", last=True)

    doc_list = []
    # Iterates through each article in the corpus.
    for doc in tqdm(newest_doc):
        # Passes that article through the pipeline and adds to a new list.
        pr = nlp(doc)
        doc_list.append(pr)

    # Creates, which is a mapping of word IDs to words.
    words = corpora.Dictionary(doc_list)

    # Turns each document into a bag of words.
    corpus = [words.doc2bow(doc) for doc in doc_list]

    lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                               id2word=words,
                                               num_topics=10, 
                                               random_state=2,
                                               update_every=1,
                                               passes=10,
                                               alpha='auto',
                                               per_word_topics=True)
    # save the model
    gensim_lda_model = datapath("saved_models/classification_model")
    lda_model.save('saved_models/classification_model/gensim_lda_model.gensim')
    content = (lda_model.print_topics(num_words=10))'''
    content = "success"
    request.session['content'] = content
    return render(request, 'document_classification/results_page.html', {'content':content})
   

        
def extract_pdf_docs(request, pk):
    if request.method == 'POST':

        doc = Classification_Documents.objects.get(pk=pk)
        documentName = str(doc.document)# get the real name of the doc
        s3BucketName = "doc-sort-file-upload"
        extract_doc_name = append_name(documentName, "pdf")
        extract_doc_name = append_name(documentName, "extracted")# create new name for extracted doc
        content = "" 

        def startJob(s3BucketName, objectName):
            response = None
            client = boto3.client('textract')
            response = client.start_document_text_detection(
            DocumentLocation={
                'S3Object': {
                    'Bucket': s3BucketName,
                    'Name': objectName
                }
            })
            return response["JobId"]

        def isJobComplete(jobId):
            time.sleep(5)
            client = boto3.client('textract')
            response = client.get_document_text_detection(JobId=jobId)
            status = response["JobStatus"]
            print("Job status: {}".format(status))
            messages.info(request, f'Job status: {status}!')

            while(status == "IN_PROGRESS"):
                time.sleep(5)
                response = client.get_document_text_detection(JobId=jobId)
                status = response["JobStatus"]
                print("Job status: {}".format(status))
                messages.info(request, f'Job status: {status}!')


            return status

        def getJobResults(jobId):

            pages = []

            time.sleep(5)

            client = boto3.client('textract')
            response = client.get_document_text_detection(JobId=jobId)
            
            pages.append(response)
            print("Resultset page recieved: {}".format(len(pages)))
            messages.info(request, f'Resultset page recieved: {len(pages)}!')

            nextToken = None
            if('NextToken' in response):
                nextToken = response['NextToken']

            while(nextToken):
                time.sleep(5)
                response = client.get_document_text_detection(JobId=jobId, NextToken=nextToken)
                pages.append(response)
                print("Resultset page recieved: {}".format(len(pages)))
                messages.info(request, f'Resultset page recieved: {len(pages)}!')
                nextToken = None
                if('NextToken' in response):
                    nextToken = response['NextToken']
            return pages


        jobId = startJob(s3BucketName, documentName)
        print("Started job with id: {}".format(jobId))
        messages.info(request, f'Started job with id: {jobId}!')
        if(isJobComplete(jobId)):
            response = getJobResults(jobId)

        # Add detected text as content
        for resultPage in response:
            for item in resultPage["Blocks"]:
                if item["BlockType"] == "LINE":
                    content += (item["Text"]+"/n ")
                    print ('\033[94m' +  item["Text"] + '\033[0m')

        # upload detected text file to s3
        s3 = boto3.resource('s3')        
        s3.Object('doc-sort-file-upload', extract_doc_name).put(Body=content)
        extraxt_doc = Classification_Documents(username=request.user, description='extracted text', document=extract_doc_name, author=request.user)
        extraxt_doc.save()
        messages.success(request, f'Document etraction and upload complete')
        return content
    else:
        messages.error(request, f'unable to extract text!')
    return render(request, 'document_classification-extract_preview_file.html')

def read_csv_doc(request, pk):
    if request.method == 'POST':# check for post request
        request.session['pk'] = pk        
        doc = Classification_Documents.objects.get(pk=pk)# get the document ref from the database
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
        content = data.head().to_dict()
        pprint(content)
        request.session['content'] = content
        
        return redirect('document_classification-display_csv_text')
    else:
        messages.error(request, f'unable to read c.s.v. file!')
    return render(request, 'document_classification-csv_preview_file.html')

def read_json_doc(request, pk):
    if request.method == 'POST':# check for post request
        request.session['pk'] = pk      
        doc = Classification_Documents.objects.get(pk=pk)# get the document ref from the database
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
        content = data.head().to_dict()
        pprint(content)
        request.session['content'] = content
        return redirect('document_classification-display_json_text')
    else:
        messages.error(request, f'unable to read json file!')
    return render(request, 'document_classification-json_preview_file.html')