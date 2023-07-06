from django.urls import path

from . import views

app_name='theotherapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('browse', views.browse_view, name='browse'),
    path('upload', views.data_upload_view, name='upload'),
    path('multiple_upload', views.multiple_data_upload_view, name='multiple_upload'),
    path('quick_search', views.quick_search_view, name='quick_search'),
    path('plot', views.plot_view, name='plot'),
    path('delete_temporary_plot_files', views.delete_temporary_plot_files, name='delete_temporary_plot_files'),
    path('advanced_search', views.advanced_search_view, name='advanced_search'),
    path('advanced_results', views.advanced_results_view, name='advanced_results'),
    path('slideshow_plot', views.slideshow_plot_view, name='slideshow_plot'),
    path('diversity_plot', views.diversity_plot_view, name='diversity_plot'),
    path('pca_view', views.pca_view, name='pca_view'),
    path('view_interactive_plot', views.view_interactive_plot, name='view_interactive_plot'),
    path('additional_files', views.additional_files_view, name='additional_files')
]

#handler404 = 'theotherapp.views.custom_page_not_found_view'
handler500 = 'theotherapp.views.custom_error_view'
handler400 = 'theotherapp.views.custom_bad_request_view'
handler403 = 'theotherapp.views.custom_permission_denied_view'