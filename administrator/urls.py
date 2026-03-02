from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    
    path('adminlogin/',views.adminlogin,name='adminlogin'),
    path('managedisease/',views.managedisease,name='managedisease'),
    path('d_save_data/',views.d_save_data,name='d_save_data'),
    path('d_display_disease/',views.d_display_disease,name='d_display_disease'),
    path('d_edit_data/<int:d_id>',views.d_edit_data,name='d_edit_data'),
    path('d_update_disease/',views.d_update_disease,name='d_update_disease'),
    path('d_delete_disease/<int:d_id>',views.d_delete_disease,name='d_delete_disease'),
    path('p_display_patients/',views.p_display_patients,name='p_display_patients'),
    path('view_patient_images/',views.view_patient_images,name='view_patient_images'),
    path('add_doctor/',views.add_doctor,name='add_doctor'),
    path('view_doctor/',views.view_doctor,name='view_doctor'),
    path('save_doctor_data/',views.save_doctor_data,name='save_doctor_data'),
    path('edit_doctor/<int:do_id>',views.edit_doctor,name='edit_doctor'),
    path('update_doctor/', views.update_doctor, name='update_doctor'),
    path('delete_doctor/<int:do_id>',views.delete_doctor,name='delete_doctor'),
    path('view_feedback/',views.view_feedback,name='view_feedback'),
    path('change_password_page/',views.change_password_page,name='change_password_page'),
    path('admin_update_pass/',views.admin_update_pass,name='admin_update_pass'),
    path('edit_doctor_img/<int:pid>/', views.edit_doctor_img, name='edit_doctor_img'),
    path('update_doctor_img/<int:pid>/', views.update_doctor_img, name='update_doctor_img'),
    path('logout',views.logout,name='logout'),
    path('dataset_insights/',views.dataset_insights,name='dataset_insights'),
]