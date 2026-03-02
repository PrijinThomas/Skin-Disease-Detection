from django.shortcuts import render,redirect
from skin_diseases import models
from django.contrib import messages
from django.utils import timezone
import re
import os
from django.conf import settings
from django.core.files.storage import default_storage


# Create your views here.
def patient_dashboard(request):
    p_email = request.session.get('semail')
    pdata = models.Patient.objects.get(patient_email=p_email)
    patient_id = pdata.patient_id

    total_images = models.SkinImages.objects.filter(fk_patient_id=patient_id).count()
    
    # Count predictions for this patient's images
    patient_image_ids = models.SkinImages.objects.filter(fk_patient_id=patient_id).values_list('skin_image_id', flat=True)
    # Since fk_skin_image_id is CharField in Predictions, we may need to handle casting if it's not consistent, 
    # but filter should work if we pass strings.
    str_image_ids = [str(sid) for sid in patient_image_ids]
    total_predictions = models.Predictions.objects.filter(fk_skin_image_id__in=str_image_ids).count()
    
    total_feedback = models.Feedback.objects.filter(fk_patient_id=patient_id).count()

    # Get recent images with diagnoses
    recent_images = models.SkinImages.objects.raw("""
        SELECT s.skin_image_id, s.image_path, s.uploaded_date, 
               d.disease_name as diagnosis, pr.confidance_score
        FROM skin_images s 
        LEFT JOIN predictions pr ON CAST(pr.fk_skin_image_id AS CHAR) = CAST(s.skin_image_id AS CHAR)
        LEFT JOIN disease d ON CAST(d.disease_id AS CHAR) = CAST(pr.fk_disease_id AS CHAR)
        WHERE s.fk_patient_id = %s
        ORDER BY s.uploaded_date DESC
        LIMIT 5
    """, [patient_id])

    context = {
        'total_images': total_images,
        'total_predictions': total_predictions,
        'total_feedback': total_feedback,
        'recent_images': recent_images,
        'pdata': pdata
    }
    return render(request, 'patient/patientdashboard.html', context)

def patient_profile(request):
    p_email=request.session['semail']
    pdata=models.Patient.objects.get(patient_email=p_email)
    context={
        'plist':pdata
    }
    return render(request,'patient/patientprofile.html',context)


def edit_patient_data(request,pid):
    pdata=models.Patient.objects.get(patient_id=pid)
    context={
        'plist':pdata
    }
    return render(request,'patient/patienteditprofile.html',context)



def update_patient_data(request, pid):

    if request.method == "POST":

        # Get current patient
        pdata = models.Patient.objects.get(patient_id=pid)

        # Get form values safely
        pa_name = request.POST.get('patient_name')
        pa_email = request.POST.get('patient_email')
        pa_address = request.POST.get('patient_address')
        pa_phone = request.POST.get('patient_phone')
        pa_gender = request.POST.get('patient_gender')
        pa_dob = request.POST.get('patient_dob')

        # ---------- PHONE VALIDATION ----------
        phone_pattern = r'^[6789]\d{9}$'
        if not re.match(phone_pattern, pa_phone):
            messages.error(request, "Phone number must be 10 digits and start with 7, 8, or 9")
            return redirect('patient_profile')

        # ---------- EMAIL FORMAT VALIDATION ----------
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, pa_email):
            messages.error(request, "Invalid email format!")
            return redirect('patient_profile')

        # ---------- EMAIL DUPLICATE CHECK (EXCLUDE CURRENT PATIENT) ----------
        if models.Patient.objects.filter(patient_email__iexact=pa_email).exclude(patient_id=pid).exists():
            messages.error(request, "Another patient with this email already exists!")
            return redirect('patient_profile')

        # ---------- UPDATE DATA ----------
        pdata.patient_name = pa_name
        pdata.patient_email = pa_email
        pdata.patient_address = pa_address
        pdata.patient_phone = pa_phone
        pdata.patient_gender = pa_gender
        pdata.patient_dob = pa_dob
        # ❌ DO NOT UPDATE patient_id

        pdata.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('patient_profile')


def change_pass_page_patient(request):
    return render(request, 'patient/patientchangepass.html')
     
def update_pass(request):
    oldpass=request.POST['o_pass']
    newpass=request.POST['n_pass']
    confirmpass=request.POST['c_pass']
    p_email=request.session['semail']
    pdata=models.Login.objects.get(user_name=p_email) #select * from login where username=value and password=value
    
    if pdata.password != oldpass:
            messages.success(request,'old password is wrong!!!')
            return render(request, 'patient/patientchangepass.html')

        
    if newpass==confirmpass:
                pdata.password =confirmpass
                pdata.save()
                messages.success(request,'password updated!!!')
                return render(request, 'patient/patientchangepass.html')

    else:
                messages.success(request,'new password and confirm password should be same!!!')
                return redirect('change_pass_page')

def add_skin_image(request):
    return render(request, 'patient/add_skin_img.html')

def save_skin_image(request):
    from skin_diseases.predictor import predictor
    # get logged-in patient
    p_email = request.session.get('semail')
    pdata = models.Patient.objects.get(patient_email=p_email)

    patient_id = pdata.patient_id   # INTEGER (matches fk_patient_id)

    skin_image = request.FILES.get('simg')
    image_path = None

    if skin_image:
        image_name = skin_image.name
        image_path = os.path.join('uploads', image_name)

        full_path = os.path.join(settings.MEDIA_ROOT, image_path)

        # create folder if not exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # save file manually
        with open(full_path, 'wb+') as destination:
            for chunk in skin_image.chunks():
                destination.write(chunk)

    
    newdata = models.SkinImages(
        fk_patient_id=patient_id,             # INTEGER FIELD
        image_path=image_path,                # STRING PATH
        uploaded_date=timezone.now().date()   # DATE
    )
    newdata.save()
    
    # ---------- MODULE 4: DISEASE PREDICTION (ROBUST CNN/OPENCV) ----------
    try:
        # Full path to the uploaded image for analysis
        upload_path = os.path.join(settings.MEDIA_ROOT, image_path)
        
        # Run prediction using OpenCV and (optionally) TensorFlow/CNN
        diagnosis_name, confidence = predictor.predict(upload_path)
        
        # Try to find the matching disease in our database
        # We use icontains for some flexibility (e.g., 'Acne' matches 'Acne Vulgaris')
        matched_disease = models.Disease.objects.filter(disease_name__icontains=diagnosis_name).first()
        
        # If no match, pick a fallback or the first one
        if not matched_disease:
            matched_disease = models.Disease.objects.first()
            
        if matched_disease:
            # Save the prediction result linked to this image
            prediction = models.Predictions(
                fk_skin_image_id=str(newdata.skin_image_id),
                fk_disease_id=str(matched_disease.disease_id),
                confidance_score=f"{confidence:.2f}",
                predicted_at=timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            prediction.save()
            messages.success(request, f"Skin image analysis complete: Detected {matched_disease.disease_name} with {confidence:.2f}% confidence.")
        else:
            messages.warning(request, "Image uploaded, but disease registry is empty.")
            
    except Exception as e:
        messages.error(request, f"Image uploaded but AI analysis failed: {str(e)}")

    return redirect('view_skin_image')


def view_skin_image(request):
    p_email = request.session.get('semail')
    pdata = models.Patient.objects.get(patient_email=p_email)
    patient_id = pdata.patient_id   
    
    # Use raw SQL to join with predictions and disease guidance data (Module 5)
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
        'slist': sdata
    }
    return render(request, 'patient/view_skin_image.html', context)


def delete_skin_image(request,s_id):
    s_data=models.SkinImages.objects.get(skin_image_id=s_id)
    s_data.delete()

    return redirect('view_skin_image')

def feedback(request):
    p_email=request.session['semail']
    pdata=models.Patient.objects.get(patient_email=p_email)
    fbdata=models.Feedback.objects.filter(fk_patient_id=pdata.patient_id)
    context={
          'fblist':fbdata
    }
    return render(request, 'patient/feedback.html',context)

def save_feedback(request):

    p_email=request.session['semail']
    pdata=models.Patient.objects.get(patient_email=p_email)

    
    patient_id=pdata.patient_id
    feedback=request.POST['feedback']
    submitted_date = timezone.now().date()

    fdata=models.Feedback(fk_patient_id=patient_id,message=feedback,submitted_date=submitted_date)
    fdata.save()
   
   
    return redirect('feedback')

def delete_feedback(request,f_id):
    f_data=models.Feedback.objects.get(feedback_id=f_id)
    f_data.delete()

    return redirect('feedback')


def viewdoctor(request):
    doctor_data=models.Doctor.objects.all()
    context={
        'dlist':doctor_data,
        'now': timezone.now()
    }
    return render(request,'patient/viewdoctor.html',context)



def book_appointment(request):
    if request.method == "POST":
        p_email = request.session.get('semail')
        if not p_email:
            messages.error(request, "Please login to book an appointment.")
            return redirect('login')

        try:
            p_data = models.Patient.objects.get(patient_email=p_email)
            doctor_id = request.POST.get('doctor_id')
            appointment_date = request.POST.get('appointment_date')
            remarks = request.POST.get('remarks', '')

            # Create appointment
            appointment = models.Appointment(
                fk_patient_id=p_data.patient_id,
                fk_doctor_id=doctor_id,
                appointment_date=appointment_date,
                remarks=remarks,
                medical_guidance='Pending'
            )
            appointment.save()

            messages.success(request, f"Appointment request sent successfully for {appointment_date}!")
        except Exception as e:
            messages.error(request, f"Failed to book appointment: {str(e)}")
        
        return redirect('viewdoctor')

    return redirect('viewdoctor')


def view_my_appointments(request):
    p_email = request.session.get('semail')
    pdata = models.Patient.objects.get(patient_email=p_email)
    
    # Raw SQL join to get doctor details for appointments
    appointments = models.Appointment.objects.raw("""
        SELECT a.*, d.doctor_name, d.specialization, d.doctor_email 
        FROM appointment a 
        JOIN doctor d ON a.fk_doctor_id = d.doctor_id 
        WHERE a.fk_patient_id = %s
        ORDER BY a.appointment_date DESC
    """, [pdata.patient_id])
    
    context = {
        'alist': appointments
    }
    return render(request, 'patient/view_my_appointments.html', context)


def view_diseases(request):
    d_data = models.Disease.objects.all()
    context = {
        'dlist': d_data
    }
    return render(request, 'patient/patient_view_disease.html', context)

