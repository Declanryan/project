from django.urls import path

from . import views

urlpatterns = [
    
    path('sentiment_import_data_type', views.sentiment_import_data_type, name='document_sentiment-sentiment_import_data_type'),
    path('sentiment_preview_data', views.sentiment_preview_data, name='document_sentiment-sentiment_preview_data'),
    path('sentiment_results_page', views.sentiment_results_page, name='document_sentiment-sentiment_results_page'),
    path('sentiment_upload_file', views.sentiment_upload_file, name='document_sentiment-sentiment_upload_file'),
    path('sentiment_select_doc/<int:pk>', views.sentiment_select_doc, name='document_sentiment-sentiment_select_doc'),
    path('sentiment_preview_data_file', views.sentiment_preview_data_file, name='document_sentiment-sentiment_preview_data_file'),
    path('sentiment_form', views.check_sentiment, name='document_sentiment-sentiment_form'),
    path('check_sentiment_csv', views.check_sentiment_csv, name='document_sentiment-check_sentiment_csv'),
    path('sentiment_documents/<int:pk>', views.sentiment_delete_docs, name='document_sentiment-sentiment_delete_docs'),
    path('sentiment_celery_example', views.sentiment_celery_example, name='document_sentiment-sentiment_celery_example'),

]