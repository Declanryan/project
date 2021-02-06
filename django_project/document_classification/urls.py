from django.urls import path

from . import views

urlpatterns = [
    
    path('', views.home, name='document_classification-home'),
    path('price_plan', views.price_plan, name='document_classification-price_plan'),
    path('choose_model', views.choose_model, name='document_classification-choose_model'),
    path('import_data_type', views.import_data_type, name='document_classification-import_data_type'),
    path('model_name', views.model_name, name='document_classification-model_name'),
    path('preview_data', views.preview_data, name='document_classification-preview_data'),
    path('results_page', views.results_page, name='document_classification-results_page'),
    path('setup_complete', views.setup_complete, name='document_classification-setup_complete'),
    path('tag_selection', views.tag_selection, name='document_classification-tag_selection'),
    path('testing', views.testing, name='document_classification-testing'),
    path('upload_confirmation', views.upload_confirmation, name='document_classification-upload_confirmation'),
    path('csv_upload_file', views.csv_upload_file, name='document_classification-csv_upload_file'),
    path('extract_upload_file', views.extract_upload_file, name='document_classification-extract_upload_file'),
    path('json_upload_file', views.json_upload_file, name='document_classification-json_upload_file'),
    path('extract_preview_file', views.extract_preview_file, name='document_classification-extract_preview_file'),
    path('extract_preview_file/<int:pk>', views.extract_preview_file, name='document_classification-extract_preview_file'),
    path('csv_preview_file', views.csv_preview_file, name='document_classification-csv_preview_file'),
    path('json_preview_file', views.json_preview_file, name='document_classification-json_preview_file'),
    path('display_extracted_text', views.display_extracted_text, name='document_classification-display_extracted_text'),
    path('display_csv_text', views.display_csv_text, name='document_classification-display_csv_text'),
    path('display_json_text', views.display_json_text, name='document_classification-display_json_text'),
    path('documents/<int:pk>', views.delete_docs, name='document_classification-delete_docs'),
    path('extract_documents/<int:pk>', views.extract_doc, name='document_classification-extract_doc'),
    path('select_doc/<int:pk>', views.select_doc, name='document_classification-select_doc'),
    path('read_csv_doc/<int:pk>', views.read_csv_doc, name='document_classification-read_csv_doc'),
    path('read_json_doc/<int:pk>', views.read_json_doc, name='document_classification-read_json_doc'),
    path('topic_extraction', views.topic_extraction, name='document_classification-topic_extraction')

]