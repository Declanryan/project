from django.urls import path

from . import views

urlpatterns = [
    
    path('summary_import_data_type', views.summary_import_data_type, name='document_summary-summary_import_data_type'),
    path('summary_preview_data', views.summary_preview_data, name='document_summary-summary_preview_data'),
    path('summary_results_page', views.summary_results_page, name='document_summary-summary_results_page'),
    path('summary_upload_file', views.summary_upload_file, name='document_summary-summary_upload_file'),
    path('summary_select_doc/<int:pk>', views.summary_select_doc, name='document_summary-summary_select_doc'),
    path('summary_preview_data_file', views.summary_preview_data_file, name='document_summary-summary_preview_data_file'),
    path('summary_form', views.check_summary, name='document_summary-summary_form'),
    path('check_summary_csv', views.check_summary_csv, name='document_summary-check_summary_csv'),
    path('summary_progress_csv', views.check_summary_csv, name='document_summary-summary_progress_csv'),
    path('summary_documents/<int:pk>', views.summary_delete_docs, name='document_summary-summary_delete_docs'),
    path('summary_celery_example', views.summary_celery_example, name='document_summary-summary_celery_example'),

]