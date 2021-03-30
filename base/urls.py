from django.conf import settings
from django.urls import path
from base import views
from base.views import RegistrationView, InputView, UserHistoryView, DeleteConvertView, DownloadView, ConfirmRegistration
from django.conf.urls.static import static


urlpatterns = [
    path('',  InputView.as_view(), name='start'),
    path('text_len', views.check_len, name='text_len'),
    path('input_text', views.ajax_input_text, name='input_text'),
    path('signup', RegistrationView.as_view(), name='signup'),
    path('history', UserHistoryView.as_view(), name='history'),
    path('delete_convert', DeleteConvertView.as_view(), name='delete_convert'),
    path('download', DownloadView.as_view(), name='download'),
    path('ajax_open_file', views.ajax_open_file, name='ajax_open_file'),
    path('upload_file', views.ajax_upload_file, name='upload_file'),
    path('convert_file', views.convert_upload_file, name='convert_file'),
    path('activate/<slug:uidb64>/<slug:token>/', views.activate, name='activate'),
    path('confirm_registration', ConfirmRegistration.as_view(), name='confirm_registration')

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)