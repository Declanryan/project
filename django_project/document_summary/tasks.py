from celery import shared_task
from celery_progress.backend import ProgressRecorder
from .forms import upload_file_form, summary_form
from .models import Summary_Documents
import boto3
from botocore.config import Config
import time, os, sys
import pandas as pd
from gensim import summarization
from gensim.summarization.summarizer import summarize
from io import StringIO

@shared_task(bind=True) # testing of progress bars
def summary_test_task(self, seconds):
    progress_recorder = ProgressRecorder(self)
    result = 0
    for i in range(seconds):
        time.sleep(1)
        result += i
        progress_recorder.set_progress(i + 1, seconds)
    return result

@shared_task(bind=True)
def summary_summarize_task(self, pk):
	''' retrive csv file from s3.
        read into datframe.
        get summaization of document
        add summary to list
        add list to dictionary
    '''
	progress_recorder = ProgressRecorder(self) # create progress recorder object  
	doc = Summary_Documents.objects.get(pk=pk)# get the document ref from the database
	documentName = str(doc.document)# get the name of the doc 
	aws_id = os.environ.get('AWS_ACCESS_KEY_ID') # aws access
	aws_secret = os.environ.get('AWS_SECRET_ACCESS_KEY') #aws access
	REGION = 'eu-west-1'
	client = boto3.client('s3', region_name = REGION, aws_access_key_id=aws_id,
	        aws_secret_access_key=aws_secret) # create the client to retrieve the file from storage
	bucket_name = "doc-sort-file-upload"
	object_key = documentName
	csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
	body = csv_obj['Body']
	csv_string = body.read().decode('utf-8')
	data = pd.read_csv(StringIO(csv_string)) # read csv into dataframe
	documents = data['content']
	docs_summarized = 0
	docs_not_summarized = 0
	total_docs = 0
	documents_len = []
	summary_len = []
	result = [] # new column to hold result integer (0,1,2)value
	count = 0
	for doc in documents:# iterate through filtered list
		documents_len.append(len(doc))
		summary = summarize(doc, ratio = 0.03) # get summary
		result.append(summary)
		summary_len.append(len(summary))
		total_docs += 1
		if result == None:
			result.append("Document too short")
			docs_not_summarized += 1
		docs_summarized += 1   
		progress_recorder.set_progress(count +1, len(documents)) # update progress
		count +=1 # update count

	
	summary_dict = {} 
	  
	# Adding list as value 
	summary_dict["Result"] = result 
	summary_dict["Total_docs"] = total_docs
	summary_dict["Docs_summarized"] = docs_summarized
	summary_dict["Docs_not_summarized"] = docs_not_summarized
	summary_dict["Documents_len"] = documents_len
	summary_dict["Summary_len"] = summary_len

	return summary_dict
