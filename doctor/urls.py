from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [

path('doctor_dashboard/',views.doctor_dashboard,name='doctor_dashboard'),
path('doctor_profile/',views.doctor_profile,name='doctor_profile'),
path('edit_doctor_data/<int:pid>',views.edit_doctor_data,name='edit_doctor_data'),
path('update_doctor_data/<int:pid>',views.update_doctor_data,name='update_doctor_data'),
path('change_pass_page/',views.change_pass_page,name='change_pass_page'),
path('update_pass/',views.update_pass,name='update_pass'),
path('edit_doctor_image/<int:pid>/', views.edit_doctor_image, name='edit_doctor_image'),
path('update_doctor_image/<int:pid>/', views.update_doctor_image, name='update_doctor_image'),


path('view_appointments/', views.view_appointments, name='view_appointments'),
path('patient_ai_data/<int:aid>/', views.patient_ai_data, name='patient_ai_data'),
path('add_medical_guidance/', views.add_medical_guidance, name='add_medical_guidance'),
path('doctor_disease_info/', views.view_diseases, name='doctor_disease_info'),
]
