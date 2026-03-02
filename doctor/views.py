from django.shortcuts import render,redirect
from skin_diseases import models
from django.contrib import messages
import re
import os
from django.conf import settings


def doctor_dashboard(request):
    d_email = request.session.get('semail')
    ddata = models.Doctor.objects.get(doctor_email=d_email)
    
    # Statistics
    total_appointments = models.Appointment.objects.filter(fk_doctor_id=ddata.doctor_id).count()
    total_patients = models.Appointment.objects.filter(fk_doctor_id=ddata.doctor_id).values('fk_patient_id').distinct().count()
    pending_guidance = models.Appointment.objects.filter(fk_doctor_id=ddata.doctor_id, medical_guidance='Pending').count()
    
    # Recent Appointments with patient names
    recent_appointments = models.Appointment.objects.raw("""
        SELECT a.*, p.patient_name, p.patient_phone 
        FROM appointment a 
        JOIN patient p ON a.fk_patient_id = p.patient_id 
        WHERE a.fk_doctor_id = %s
        ORDER BY a.appointment_date DESC
        LIMIT 5
    """, [ddata.doctor_id])
    
    context = {
        'total_appointments': total_appointments,
        'total_patients': total_patients,
        'pending_guidance': pending_guidance,
        'recent_appointments': recent_appointments,
        'ddata': ddata
    }
    return render(request, 'doctor/doctor_dashboard.html', context)




def doctor_profile(request):
    p_email=request.session['semail']
    pdata=models.Doctor.objects.get(doctor_email=p_email)
    context={
        'plist':pdata
    }
    return render(request,'doctor/doctorprofile.html',context)


def edit_doctor_data(request,pid):
    pdata=models.Doctor.objects.get(doctor_id=pid)
    context={
        'plist':pdata
    }
    return render(request,'doctor/doctoreditprofile.html',context)

def update_doctor_data(request,pid):
    
        pdata = models.Doctor.objects.get(doctor_id=pid)

        pdata.doctor_name_name = request.POST['doctor_name']
        pdata.doctor_email = request.POST['doctor_email']

        pdata.doctor_phone = request.POST['doctor_phone']
        pdata.specialization = request.POST['specialization']
        pdata.experience = request.POST['experience']
        pdata.doctor_id = request.POST['doctor_id']

        phone_pattern = r'^[6789]\d{9}$'
        if not re.match(phone_pattern, pdata.doctor_phone):
            messages.error(request, "Phone number must be 10 digits and start with 7, 8, or 9")
            return redirect('doctor_profile') 
        
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, pdata.doctor_email):
            messages.error(request, "Invalid email format!")
            return redirect('doctor_profile')
        
        if models.Doctor.objects.filter(doctor_email=pdata.doctor_email).exclude(doctor_id=pdata.doctor_id).exists():
            messages.error(request, "Another doctor with this email already exists!")
            return redirect('doctor_profile')

        pdata.save()
        messages.success(request, "Doctor updated successfully!")
        return redirect('doctor_profile')


def change_pass_page(request):
    return render(request, 'doctor/doctor_change_pass.html')
     
def update_pass(request):
    oldpass=request.POST['o_pass']
    newpass=request.POST['n_pass']
    confirmpass=request.POST['c_pass']
    p_email=request.session['semail']
    pdata=models.Login.objects.get(user_name=p_email) #select * from login where username=value and password=value
    
    if pdata.password != oldpass:
            messages.success(request,'old password is wrong!!!')
            return render(request, 'doctor/doctor_change_pass.html')

        
    if newpass==confirmpass:
                pdata.password =confirmpass
                pdata.save()
                messages.success(request,'password updated!!!')
                return render(request, 'doctor/doctor_change_pass.html')

    else:
                messages.success(request,'new password and confirm password should be same!!!')
                return redirect('change_pass_page')
    



def edit_doctor_image(request, pid):
    pdata = models.Doctor.objects.get(doctor_id=pid)

    context = {
        'plist': pdata
    }
    return render(request, 'doctor/edit_doctor_image.html', context)


def update_doctor_image(request, pid):

    pdata = models.Doctor.objects.get(doctor_id=pid)

    new_img = request.FILES.get('do_img')

    if not new_img:
        messages.error(request, "Please select an image to update.")
        return redirect('change_doctor_image', pid)

    image_name = new_img.name
    image_path = os.path.join('doctor_uploads', image_name)

    full_path = os.path.join(settings.MEDIA_ROOT, image_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, 'wb+') as destination:
        for chunk in new_img.chunks():
            destination.write(chunk)


    if pdata.doctor_img:
        old_path = os.path.join(settings.MEDIA_ROOT, pdata.doctor_img)
        if os.path.exists(old_path):
            os.remove(old_path)

   
    pdata.doctor_img = image_path
    pdata.save()


    messages.success(request, "Doctor image updated successfully!")
    return redirect('doctor_profile')


def view_appointments(request):
    d_email = request.session.get('semail')
    ddata = models.Doctor.objects.get(doctor_email=d_email)
    
    # Raw SQL join to get patient details for appointments
    appointments = models.Appointment.objects.raw("""
        SELECT a.*, p.patient_name, p.patient_phone, p.patient_email 
        FROM appointment a 
        JOIN patient p ON a.fk_patient_id = p.patient_id 
        WHERE a.fk_doctor_id = %s
        ORDER BY a.appointment_date DESC
    """, [ddata.doctor_id])
    
    context = {
        'alist': appointments
    }
    return render(request, 'doctor/view_appointments.html', context)


def patient_ai_data(request, aid):
    # This view shows the patient's predicted data for a specific appointment
    appointment = models.Appointment.objects.get(appointment_id=aid)
    patient_id = appointment.fk_patient_id
    pdata = models.Patient.objects.get(patient_id=patient_id)
    
    # Get all skin images and predictions for this patient
    sdata = models.SkinImages.objects.raw("""
        SELECT s.skin_image_id, s.image_path, s.uploaded_date, 
               d.disease_name as diagnosis, pr.confidance_score,
               d.description, d.symptoms, d.precautions
        FROM skin_images s 
        LEFT JOIN predictions pr ON CAST(pr.fk_skin_image_id AS CHAR) = CAST(s.skin_image_id AS CHAR)
        LEFT JOIN disease d ON CAST(d.disease_id AS CHAR) = CAST(pr.fk_disease_id AS CHAR)
        WHERE s.fk_patient_id = %s
        ORDER BY s.uploaded_date DESC
    """, [patient_id])
    
    context = {
        'slist': sdata,
        'pdata': pdata,
        'appointment': appointment
    }
    return render(request, 'doctor/patient_ai_data.html', context)


def add_medical_guidance(request):
    if request.method == "POST":
        aid = request.POST.get('appointment_id')
        guidance = request.POST.get('medical_guidance')
        
        appointment = models.Appointment.objects.get(appointment_id=aid)
        appointment.medical_guidance = guidance
        appointment.save()
        
        messages.success(request, "Medical guidance added successfully!")
        return redirect('view_appointments')
    return redirect('view_appointments')

def view_diseases(request):
    d_data = models.Disease.objects.all()
    context = {
        'dlist': d_data
    }
    return render(request, 'doctor/doctor_view_disease.html', context)
