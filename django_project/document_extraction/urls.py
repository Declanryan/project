from django.urls import path

from . import views

urlpatterns = [
    
    path('extraction_import_data_type', views.extraction_import_data_type, name='document_extraction-extraction_import_data_type'),
    path('extraction_upload_file', views.extraction_upload_file, name='document_extraction-extraction_upload_file'),
    path('extraction_preview_file', views.extraction_preview_file, name='document_extraction-extraction_preview_file'),
    path('extraction_add_to_file', views.extraction_add_to_file, name='document_extraction-extraction_add_to_file'),
    path('extraction_preview_file/<int:pk>', views.extraction_preview_file, name='document_extraction-extraction_preview_file'),
    path('extraction_display_extracted_text', views.extraction_display_extracted_text, name='document_extraction-extraction_display_extracted_text'),
    path('extraction_documents/<int:pk>', views.extraction_delete_docs, name='document_extraction-extraction_delete_docs'),
    path('extraction_extract_documents/<int:pk>', views.extraction_extract_doc, name='document_extraction-extraction_extract_doc'),
    path('extraction_select_doc/<int:pk>', views.extraction_select_doc, name='document_extraction-extraction_select_doc'),

]