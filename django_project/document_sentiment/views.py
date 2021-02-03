from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from .forms import upload_file_form, sentiments_form
from .models import Sentiment_Documents
import boto3
from botocore.config import Config
import time
from collections import OrderedDict
from .fusioncharts import FusionCharts
import stanza
import spacy
from spacy import displacy
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
            # predictions = DocumentSentimentConfig.sample_predict(sample_pred_text, pad=True)
            # result = int(predictions[0][0] * 100)
            nlp = stanza.Pipeline(lang='en', processors='tokenize,sentiment')
            doc = nlp(sample_pred_text)
            for i, sentence in enumerate(doc.sentences):
                print(i, sentence.sentiment)
                result = sentence.sentiment
            form.sentiment = result
            form.save()
            messages.success(request, f'The detected sentiment is {result}!')
            request.session['result'] = result
            request.session['sample_pred_text'] = sample_pred_text
            return redirect('document_sentiment-sentiment_results_page')          
    else:
        form = sentiments_form()
    return render(request, 'document_sentiment/sentiments_form.html', {'form': form})   
    

def delete_docs(request, pk):
    if request.method == 'POST':
        doc = Sentiment_Documents.objects.get(pk=pk)
        doc.delete()
    return redirect('document_sentiment-preview_data')

def sentiment_results_page(request):
    result = request.session['result']# define result
    sample_pred_text = request.session['sample_pred_text']

    # start spacy_doc
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
    widgetConfig["upperLimit"] = "100"
    widgetConfig["showValue"] = "1"
    widgetConfig["numberSuffix"] = "%"
    widgetConfig["theme"] = "candy"
    widgetConfig["showToolTip"] = "0"

    # The `colorData` dict contains key-value pairs of data for ColorRange of dial
    colorRangeData = OrderedDict()
    colorRangeData["color"] = [{
            "minValue": "0",
            "maxValue": "50",
            "code": "#F2726F"
        },
        {
            "minValue": "50",
            "maxValue": "75",
            "code": "#FFC533"
        },
        {
            "minValue": "75",
            "maxValue": "100",
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