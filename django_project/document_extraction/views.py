from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .forms import upload_file_form
from .models import Extraction_Documents
import boto3, botocore
from botocore.config import Config
import time, os, sys
from smart_open import open
from io import StringIO
import numpy as np
import pandas as pd


@login_required
def extraction_import_data_type(request):
    return render(request, 'document_extraction/extraction_import_data_type.html')


@login_required
def extraction_upload_file(request):
    if request.method == 'POST':
        form = upload_file_form(request.POST, request.FILES)
        form.instance.author = request.user
        if form.is_valid():
            form.save()
            return redirect('document_extraction-extraction_preview_file')
    else:
        form = upload_file_form()
    return render(request, 'document_extraction/extraction_upload_file.html', {'form': form})


@login_required
def extraction_preview_file(request):
    docs = Extraction_Documents.objects.filter(author=request.user.id)
    return render(request, 'document_extraction/extraction_preview_file.html', {'docs':docs})

@login_required
def extraction_delete_docs(request, pk):
    if request.method == 'POST':
        doc = Extraction_Documents.objects.get(pk=pk)
        doc.delete()
    return redirect('document_extraction-extraction_preview_file')

def extraction_append_name(filename, type):
    name, ext = os.path.splitext(filename)# split the filename
    return "{file_name}_{text}{ext}".format(file_name=name, text=type, ext=".txt")# add extracted to name and .txt extension

def extraction_check_extension(filename):
    name, ext = os.path.splitext(filename)# split the filename
    if ext == '.pdf':
        return '.pdf'
    else:
        return '.other'

def extraction_check_file(request, pk, filename):
    name, ext = os.path.splitext(filename)# split the filename

    if ext == '.csv':
        request.session['pk'] = pk        
        doc = Extraction_Documents.objects.get(pk=pk)# get the document ref from the database
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
        #pprint(content) # testing
        request.session['content'] = content
        return '.csv'

    elif ext == '.txt':
        request.session['pk'] = pk        
        doc = Extraction_Documents.objects.get(pk=pk)# get the document ref from the database
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
        # pprint(content) # testing
        request.session['content'] = content
        return '.txt'

    else:
        return '.other'

@login_required
def extraction_select_doc(request, pk):
    if request.method == 'POST':# check for post request
        doc = Extraction_Documents.objects.get(pk=pk)# get the document ref from the database
        documentName = str(doc.document)# get the real name of the doc
        ext = extraction_check_file(request, pk, documentName)
        if ext == '.other': # check if doc is unsupported format
            messages.error(request, f'Please use an extracted file format such as .txt, .csv or begin extraction process on a new file')
            return redirect('document_extraction-extraction_preview_file')
        else:
            return redirect('document_extraction-extraction_display_extracted_text')
    else:
        messages.error(request, f'unable to process file')
    return render(request, 'document_extraction-extraction_preview_file.html')
    
@login_required
def extraction_extract_doc(request, pk):
    if request.method == 'POST':# check for post request
        doc = Extraction_Documents.objects.get(pk=pk)# get the document ref from the database
        documentName = str(doc.document)# get the real name of the doc
        ext = extraction_check_extension(documentName)
        request.session['pk'] = pk
        if ext == '.pdf': # check if doc is a pdf
            extract_doc_name = extraction_append_name(documentName, "extracted")# create new name for extracted doc
            content = extract_pdf_docs(request, pk)
            request.session['content'] = content
            s3 = boto3.resource('s3')        
            s3.Object('doc-sort-file-upload', extract_doc_name).put(Body=content)
            extraxt_doc = Extraction_Documents(username=request.user, description='extracted text', document=extract_doc_name, author=request.user)
            extraxt_doc.save()
            return redirect('document_extraction-extraction_display_extracted_text')
        else:
            extract_doc_name = extraction_append_name(documentName, "extracted")# create new name for extracted doc
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
            extraxt_doc = Extraction_Documents(username=request.user, description='extracted text', document=extract_doc_name, author=request.user)
            extraxt_doc.save()
            request.session['content'] = content
            return redirect('document_extraction-extraction_display_extracted_text')
    else:
        messages.error(request, f'unable to extract text!')
    return render(request, 'document_extraction-extraction__preview_file.html')


@login_required
def extraction_display_extracted_text(request):
    docs = Extraction_Documents.objects.filter(author=request.user.id, document__contains="extracted")
    return render(request, 'document_extraction/extraction_display_extracted_text.html', {'docs':docs})


def extract_pdf_docs(request, pk):
    if request.method == 'POST':

        doc = Extraction_Documents.objects.get(pk=pk)
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
            

            while(status == "IN_PROGRESS"):
                time.sleep(5)
                response = client.get_document_text_detection(JobId=jobId)
                status = response["JobStatus"]
                print("Job status: {}".format(status))
               


            return status

        def getJobResults(jobId):

            pages = []

            time.sleep(5)

            client = boto3.client('textract')
            response = client.get_document_text_detection(JobId=jobId)
            
            pages.append(response)
            print("Resultset page recieved: {}".format(len(pages)))
           

            nextToken = None
            if('NextToken' in response):
                nextToken = response['NextToken']

            while(nextToken):
                time.sleep(5)
                response = client.get_document_text_detection(JobId=jobId, NextToken=nextToken)
                pages.append(response)
                print("Resultset page recieved: {}".format(len(pages)))
                nextToken = None
                if('NextToken' in response):
                    nextToken = response['NextToken']
            return pages


        jobId = startJob(s3BucketName, documentName)
        print("Started job with id: {}".format(jobId))
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
        extraxt_doc = Extraction_Documents(username=request.user, description='extracted text', document=extract_doc_name, author=request.user)
        extraxt_doc.save()
        messages.success(request, f'Document extraction and upload complete')
        return content
    else:
        messages.error(request, f'unable to extract text!')
    return render(request, 'document_extraction_-extract_preview_file.html')