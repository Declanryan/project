from django.urls import path

from . import views

urlpatterns = [
    
    path('import_data_type', views.import_data_type, name='document_sentiment-import_data_type'),
    path('preview_data', views.preview_data, name='document_sentiment-preview_data'),
    path('sentiment_results_page', views.sentiment_results_page, name='document_sentiment-sentiment_results_page'),
    path('upload_confirmation', views.upload_confirmation, name='document_sentiment-upload_confirmation'),
    path('upload_file', views.upload_file, name='document_sentiment-upload_file'),
    path('sentiments_form', views.check_sentiment, name='document_sentiment-sentiments_form'),
    path('documents/<int:pk>', views.delete_docs, name='document_sentiment-delete_docs'),

]