from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import tag_selection_form, model_name_selection_form, upload_file_form
from .models import Classification_Documents
import boto3, botocore
from botocore.config import Config
import time, os
from tempfile import NamedTemporaryFile
from smart_open import open
from collections import defaultdict
from gensim import corpora
from gensim.parsing.preprocessing import preprocess_string
from gensim import corpora, models,similarities
from gensim.models import Word2Vec

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
            return redirect('document_classification/results_page.html')
    else:
        form = tag_selection_form()
        return render(request, 'document_classification/tag_selection.html', {'form': form})

def testing(request): 
    return render(request, 'document_classification/testing.html')

def extract_upload_file(request):
    if request.method == 'POST':
        print(request)
        form = upload_file_form(request.POST, request.FILES)
        form.instance.author = request.user
        if form.is_valid():
            form.save()
            return redirect('document_classification-extract_preview_file')
    else:
        form = upload_file_form()
    return render(request, 'document_classification/extract_upload_file.html', {'form': form})


def upload_file(request):
    if request.method == 'POST':
        form = upload_file_form(request.POST, request.FILES)
        form.instance.author = request.user
        if form.is_valid():
            form.save()
            return redirect('document_classification-preview_data')
    else:
        form = upload_file_form()
    return render(request, 'document_classification/upload_file.html', {'form': form})


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

def extract_doc(request, pk):
    if request.method == 'POST':# check for post request
        doc = Classification_Documents.objects.get(pk=pk)# get the document ref from the database
        documentName = str(doc.document)# get the real name of the doc
        ext = check_extension(documentName)
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

def topic_extraction(request):
    content = request.session['content']# define content
    sentences = [["I", "am", "trying", "to", "understand", "Natural", 
              "Language", "Processing"],
            ["Natural", "Language", "Processing", "is", "fun", 
             "to", "learn"],
            ["There", "are", "numerous", "use", "cases", "of", 
             "Natural", "Language", "Processing"]]
     # model = Word2Vec(sentences, min_count=1)

        
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
            messages.success(request, f'Job status: {status}!')

            while(status == "IN_PROGRESS"):
                time.sleep(5)
                response = client.get_document_text_detection(JobId=jobId)
                status = response["JobStatus"]
                print("Job status: {}".format(status))
                messages.success(request, f'Job status: {status}!')


            return status

        def getJobResults(jobId):

            pages = []

            time.sleep(5)

            client = boto3.client('textract')
            response = client.get_document_text_detection(JobId=jobId)
            
            pages.append(response)
            print("Resultset page recieved: {}".format(len(pages)))
            messages.success(request, f'Resultset page recieved: {len(pages)}!')

            nextToken = None
            if('NextToken' in response):
                nextToken = response['NextToken']

            while(nextToken):
                time.sleep(5)
                response = client.get_document_text_detection(JobId=jobId, NextToken=nextToken)
                pages.append(response)
                print("Resultset page recieved: {}".format(len(pages)))
                messages.success(request, f'Resultset page recieved: {len(pages)}!')
                nextToken = None
                if('NextToken' in response):
                    nextToken = response['NextToken']
            return pages


        jobId = startJob(s3BucketName, documentName)
        print("Started job with id: {}".format(jobId))
        messages.success(request, f'Started job with id: {jobId}!')
        if(isJobComplete(jobId)):
            response = getJobResults(jobId)

        # Add detected text to a file
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