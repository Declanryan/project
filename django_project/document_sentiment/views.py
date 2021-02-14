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
from .fusioncharts import FusionCharts
import stanza
import spacy
from spacy import displacy
from io import StringIO
from pprint import pprint
my_stopwords = ['I', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]

def remove_mystopwords(sentence):
    tokens = sentence.split(" ")
    tokens_filtered= [word for word in tokens if not word in my_stopwords]
    return (" ").join(tokens_filtered)


def create_filter_list(data):
    filter_list = []
    for row in data['content']:
      row = remove_mystopwords(row)
      filter_list.append(row)
    return filter_list


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
            form.save()
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

@login_required
def check_sentiment_csv(request):
    ''' retrive csv file from s3.
        read into datframe.
        filter stop words
        apply sentiment analysis
        add result to original df
    '''
    if request.method == 'POST':
        try:
            pk =  request.session['pk']# get the file key       
            doc = Sentiment_Documents.objects.get(pk=pk)# get the document ref from the database
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
            nlp = stanza.Pipeline(lang='en', processors='tokenize, sentiment')# initiate stanza pipeline
            filter_list = create_filter_list(data) # remove stop words from sentences and create a list of the filterd sentences
            result = [] # new colum to hold result integer (0,1,2)value
            result_str = [] # new column to hold result string value
            
            for row in filter_list:# iterate through filtered list
                print("row-", row)
                doc = nlp(row) # send sentence trough the pipeline 
                print("doc-", doc)
                for i, sentence in enumerate(doc.sentences): # iterate through each sentence and break it down to words then apply sentiment to each
                    print(row,i, sentence.sentiment) # testing
                    result.append(sentence.sentiment) # add value to result column
                    if sentence.sentiment == 0: # check value and add appropiate string value
                        result_str.append("Negative") 
                    elif sentence.sentiment == 1:
                        result_str.append("Neutral")
                    else:
                        result_str.append("Positive")

            #print(result) # testing
            #print(result_str) # testing
            data["Result"] = result # Add result column to dataframe
            data["Result_Label"] = result_str # Add label result to dataframe
            # data.head(5) # testing 
            request.session['result'] = 2
            request.session['sample_pred_text'] = "sample pred text"
            return redirect('document_sentiment-sentiment_results_page')
        except:
            messages.error(request, f'unable to process file')
            docs = Sentiment_Documents.objects.filter(author=request.user.id)
            return render(request, 'document_sentiment/sentiment_preview_data_file.html', {'docs':docs})

    else:
        docs = Sentiment_Documents.objects.filter(author=request.user.id)
        return render(request, 'document_sentiment/sentiment_preview_data_file.html', {'docs':docs})

@login_required
def sentiment_preview_data_file(request):
    docs = Sentiment_Documents.objects.filter(author=request.user.id)
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
        content = data.head().to_dict()
        pprint(content)
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
        # content = file.read().replace("\n", " ")
        pprint(content)
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
    result = request.session['result']# define result
    sample_pred_text = request.session['sample_pred_text']

    # Load English tokenizer, tagger, parser, NER and word vectors
    nlp = spacy.load("en_core_web_md")

    # Process whole documents
    text = (sample_pred_text)
    doc = nlp(text)
    doc_result = ""
    # Analyze syntax
    print("Noun phrases:", [chunk.text for chunk in doc.noun_chunks])
    print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "VERB"])

    # Find named entities, phrases and concepts
    #for entity in doc.ents:
     #   print(entity.text, entity.label_)

    # end spacy_doc
    #---------------------------------------------------------------

    # begin chart
    chart_dataSource = OrderedDict()
    chart_dataSource["data"] = []
     # The data for the chart should be in an array wherein each element of the array  is a JSON object having the `label` and `value` as keys.

    chart_dataSource["data"].append({"label": 'Venezuela', "value": '290'})
    chart_dataSource["data"].append({"label": 'Saudi', "value": '290'})
    chart_dataSource["data"].append({"label": 'Canada', "value": '180'})
    chart_dataSource["data"].append({"label": 'Iran', "value": '140'})
    chart_dataSource["data"].append({"label": 'Russia', "value": '115'})
    chart_dataSource["data"].append({"label": 'Russia', "value": '115'})
    chart_dataSource["data"].append({"label": 'UAE', "value": '100'})
    chart_dataSource["data"].append({"label": 'US', "value": '30'})
    chart_dataSource["data"].append({"label": 'China', "value": '30'})

    # The `chartConfig` dict contains key-value pairs of data for chart attribute

    chartConfig = OrderedDict()
    chartConfig["caption"] = "Nordstrom's Customer Satisfaction Score for 2017"
    chartConfig["subCaption"] = "In MMbbl = One Million barrels"
    chartConfig["xAxisName"] = "Country"
    chartConfig["yAxisName"] = "Reserves (MMbbl)"
    chartConfig["numberSuffix"] = "K"
    chartConfig["theme"] = "candy"

    chart_dataSource["chart"] = chartConfig
    # Create an object for the column 2D chart using the FusionCharts class constructor
    # The chart data is passed to the `chart_dataSource` parameter.
    
    column2D = FusionCharts("column2d", "myFirstChart", "450", "270", "chart-1", "json", chart_dataSource)
    
    # end chart
    #-------------------------------------------------------------

    # begin gauge
    #Load dial indicator values from simple string array# e.g.dialValues = ["52", "10", "81", "95"]
    dialValues = [result]

    # widget data is passed to the `dataSource` parameter, as dict, in the form of key-value pairs.
    gauge_dataSource = OrderedDict()

    # The `widgetConfig` dict contains key-value pairs of data for widget attribute
    widgetConfig = OrderedDict()
    widgetConfig["caption"] = "Result of sentiment analysis"
    widgetConfig["lowerLimit"] = "0"
    widgetConfig["upperLimit"] = "2"
    widgetConfig["showValue"] = "1"
    widgetConfig["numberSuffix"] = ""
    widgetConfig["theme"] = "candy"
    widgetConfig["showToolTip"] = "0"

    # The `colorData` dict contains key-value pairs of data for ColorRange of dial
    colorRangeData = OrderedDict()
    colorRangeData["color"] = [{
            "minValue": "0",
            "maxValue": "0.66",
            "code": "#F2726F"
        },
        {
            "minValue": "0.66",
            "maxValue": "1.33",
            "code": "#FFC533"
        },
        {
            "minValue": "1.33",
            "maxValue": "2",
            "code": "#62B58F"
        }
    ]

    # Convert the data in the `dialData` array into a format that can be consumed by FusionCharts.
    dialData = OrderedDict()
    dialData["dial"] = []

    gauge_dataSource["chart"] = widgetConfig
    gauge_dataSource["colorRange"] = colorRangeData
    gauge_dataSource["dials"] = dialData

    # Iterate through the data in `dialValues` and insert into the `dialData["dial"]` list.
    # The data for the `dial`should be in an array wherein each element of the
    # array is a JSON object# having the `value` as keys.
    for i in range(len(dialValues)):
        dialData["dial"].append({
        "value": dialValues[i]
    })
    # Create an object for the angular-gauge using the FusionCharts class constructor
    # The widget data is passed to the `gauge_dataSource` parameter.
    angulargaugeWidget = FusionCharts("angulargauge", "ex1", "450", "270", "gauge-1", "json", gauge_dataSource)
    # end gauge

    # returning complete JavaScript and HTML code, which is used to generate widget in the browsers.
    return render(request, 'document_sentiment/sentiment_results_page.html', {'gauge_output' : angulargaugeWidget.render(), 'chart_output': column2D.render(), 'spacy_output' : doc, 'displacy_output':displacy.parse_deps(doc)})