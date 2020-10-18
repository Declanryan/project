from django.urls import path

from . import views

urlpatterns = [
    
    path('', views.home, name='document_classification-home'),
    path('choose_model', views.choose_model, name='document_classification-choose_model'),
    path('import_data_type', views.import_data_type, name='document_classification-import_data_type'),
    path('model_name', views.model_name, name='document_classification-model_name'),
    path('preview_data', views.preview_data, name='document_classification-preview_data'),
    path('results_page', views.results_page, name='document_classification-results_page'),
    path('setup_complete', views.setup_complete, name='document_classification-setup_complete'),
    path('tag_selection', views.tag_selection, name='document_classification-tag_selection'),
    path('testing', views.testing, name='document_classification-testing'),
    path('upload_confirmation', views.upload_confirmation, name='document_classification-upload_confirmation'),
    path('upload_file', views.upload_file, name='document_classification-upload_file'),
    path('extract_upload_file', views.extract_upload_file, name='document_classification-extract_upload_file'),
    path('extract_preview_file', views.extract_preview_file, name='document_classification-extract_preview_file'),
    path('display_extracted_text', views.display_extracted_text, name='document_classification-display_extracted_text'),
    path('documents/<int:pk>', views.delete_docs, name='document_classification-delete_docs'),
    path('extract_documents/<int:pk>', views.extract_doc, name='document_classification-extract_doc'),
    path('topic_extraction', views.topic_extraction, name='document_classification-topic_extraction'),

]