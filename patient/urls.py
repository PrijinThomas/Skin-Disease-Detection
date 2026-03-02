from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [

path('patient_dashboard/',views.patient_dashboard,name='patient_dashboard'),
path('patient_profile/',views.patient_profile,name='patient_profile'),
path('edit_patient_data/<int:pid>',views.edit_patient_data,name='edit_patient_data'),
path('update_patient_data/<int:pid>',views.update_patient_data,name='update_patient_data'),
path('change_pass_page_patient/',views.change_pass_page_patient,name='change_pass_page_patient'),
path('update_pass/',views.update_pass,name='update_pass'),
path('add_skin_image/',views.add_skin_image,name='add_skin_image'),
path('save_skin_image/',views.save_skin_image,name='save_skin_image'),
path('view_skin_image/',views.view_skin_image,name='view_skin_image'),
path('delete_skin_image/<int:s_id>',views.delete_skin_image,name='delete_skin_image'),
path('feedback/',views.feedback,name='feedback'),
path('save_feedback/',views.save_feedback,name='save_feedback'),
path('delete_feedback/<int:f_id>',views.delete_feedback,name='delete_feedback'),
path('viewdoctor/',views.viewdoctor,name='viewdoctor'),

path('book_appointment/',views.book_appointment,name='book_appointment'),
path('view_my_appointments/',views.view_my_appointments,name='view_my_appointments'),
path('patient_disease_info/',views.view_diseases,name='patient_disease_info'),
# reload trigger
]


