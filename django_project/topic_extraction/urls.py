from django.urls import path

from . import views

urlpatterns = [
    
    
    path('topic_import_data_type', views.topic_import_data_type, name='topic_extraction-topic_import_data_type'),
    path('topic_preview_data', views.topic_preview_data, name='topic_extraction-topic_preview_data'),
    path('topic_results_page', views.topic_results_page, name='topic_extraction-topic_results_page'),
    path('topic_csv_upload_file', views.topic_csv_upload_file, name='topic_extraction-topic_csv_upload_file'),
    path('topic_json_upload_file', views.topic_json_upload_file, name='topic_extraction-topic_json_upload_file'),
    path('topic_csv_preview_file', views.topic_csv_preview_file, name='topic_extraction-topic_csv_preview_file'),
    path('topic_json_preview_file', views.topic_json_preview_file, name='topic_extraction-topic_json_preview_file'),
    path('topic_display_csv_text', views.topic_display_csv_text, name='topic_extraction-topic_display_csv_text'),
    path('topic_display_json_text', views.topic_display_json_text, name='topic_extraction-topic_display_json_text'),
    path('topic_documents/<int:pk>', views.topic_delete_docs, name='topic_extraction-topic_delete_docs'),
    path('topic_select_doc/<int:pk>', views.topic_select_doc, name='topic_extraction-topic_select_doc'),
    path('topic_read_csv_doc/<int:pk>', views.topic_read_csv_doc, name='topic_extraction-topic_read_csv_doc'),
    path('topic_read_json_doc/<int:pk>', views.topic_read_json_doc, name='topic_extraction-topic_read_json_doc'),
    path('topic_progress_csv', views.topic_extraction, name='topic_extraction-topic_progress_csv'),
    path('topic_extraction', views.topic_extraction, name='topic_extraction-topic_extraction')

]