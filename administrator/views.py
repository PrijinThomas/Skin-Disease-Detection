from django.shortcuts import render,redirect
from skin_diseases import models
from django.contrib import messages
import re
from django.conf import settings
import os

# Create your views here.
#admin page login
def adminlogin(request):
    doctor_count = models.Doctor.objects.count()
    patient_count = models.Patient.objects.count()
    disease_count = models.Disease.objects.count()
    feedback_count = models.Feedback.objects.count()
    
    # Fetch CNN Model performance details
    model_stats = models.ModelDetails.objects.last()
    
    # If no model record exists, provide placeholders
    if not model_stats:
        model_stats = {
            'model_name': 'CNN-VGG16',
            'accuracy': 94.2,
            'loss': 0.12,
            'trained_on': '2026-01-15',
            'dataset_used': 'HAM10000 / ISIC'
        }
    
    context = {
        'doctor_count': doctor_count,
        'patient_count': patient_count,
        'disease_count': disease_count,
        'feedback_count': feedback_count,
        'model_stats': model_stats,
    }
    return render(request, 'admin/admin.html', context)

#dataset insights
def dataset_insights(request):
    # Metadata about the datasets used in the project
    datasets = [
        {
            'name': 'HAM10000 Dataset',
            'full_name': 'Human Against Machine with 10000 training images',
            'total_images': '10,015',
            'classes': '7 (Melanoma, Melanocytic Nevi, etc.)',
            'source': 'Harvard Dataverse',
            'description': 'A large collection of multi-source dermatoscopic images of common pigmented skin lesions.'
        },
        {
            'name': 'ISIC Archive',
            'full_name': 'International Skin Imaging Collaboration',
            'total_images': '30,000+',
            'classes': 'Multiple (Acne, Eczema, Psoriasis, etc.)',
            'source': 'ISIC-Archive.com',
            'description': 'An open-source archive of skin images for training AI to detect skin cancer and other conditions.'
        }
    ]
    
    context = {
        'datasets': datasets
    }
    return render(request, 'admin/dataset_insights.html', context)

#add/manage disease (Combined Add and View)
def managedisease(request):
    d_data = models.Disease.objects.all()
    context = {
        'dlist': d_data
    }
    return render(request, 'admin/disease.html', context)
#save the added disease
def d_save_data(request):

    if request.method == "POST":
        d_name = request.POST['diseasename']
        d_description = request.POST['description']
        d_symptoms = request.POST['symptoms']
        d_prescriptions = request.POST['precuations']

        # Check if disease already exists (case-insensitive)
        if models.Disease.objects.filter(disease_name=d_name).exists():
            messages.error(request, "Disease already exists!")
            return redirect('managedisease')

        # Save only if not exists
        sdata = models.Disease(
            disease_name=d_name,
            description=d_description,
            symptoms=d_symptoms,
            precautions=d_prescriptions
        )
        sdata.save()

        messages.success(request, "Disease added successfully!")
        return redirect('managedisease')
    

#display the new disease(view disease in sidebar)
def d_display_disease(request):

    d_data=models.Disease.objects.all()
    context={
        'dlist':d_data
    }
    return render(request,'admin/diseaseview.html',context)


def d_edit_data(request,d_id):
    d_data=models.Disease.objects.get(disease_id=d_id)
    context={'dlist':d_data
    }
    return render(request, 'admin/updatedisease.html',context)


def d_update_disease(request):
    if request.method == "POST":
        disease_id = request.POST['disease_id']
        d_name = request.POST['diseasename']
        d_description = request.POST['description']
        d_symptoms = request.POST['symptoms']
        d_precautions = request.POST['precuations']

        
        d_data = models.Disease.objects.get(disease_id=disease_id)

        if models.Disease.objects.filter(disease_name=d_name).exclude(disease_id=disease_id).exists():
            messages.error(request, "Another disease with this name already exists!")
            return redirect('d_display_disease') 

    
        d_data.disease_name = d_name
        d_data.description = d_description
        d_data.symptoms = d_symptoms
        d_data.precautions = d_precautions

        d_data.save()
        messages.success(request, "Disease updated successfully!")
        return redirect('d_display_disease')

def d_delete_disease(request,d_id):
    d_data=models.Disease.objects.get(disease_id=d_id)
    d_data.delete()

    return redirect('d_display_disease')

def p_display_patients(request):
    p_data=models.Patient.objects.all()
    
    context={
        'plist':p_data
    }

    return render(request, 'admin/patientview.html',context)

def view_patient_images(request):
    # Fetch skin images joined with patient names and predicted disease (our "image description")
    images = models.SkinImages.objects.raw("""
        SELECT s.skin_image_id, s.image_path, s.uploaded_date, 
               p.patient_name, d.disease_name as diagnosis, pr.confidance_score
        FROM skin_images s 
        JOIN patient p ON p.patient_id = s.fk_patient_id
        LEFT JOIN predictions pr ON CAST(pr.fk_skin_image_id AS CHAR) = CAST(s.skin_image_id AS CHAR)
        LEFT JOIN disease d ON CAST(d.disease_id AS CHAR) = CAST(pr.fk_disease_id AS CHAR)
        ORDER BY s.uploaded_date DESC
    """)
    
    context = {
        'slist': images
    }
    return render(request, 'admin/view_patient_images.html', context)

def add_doctor(request):
    return render(request,'admin/add_doctor.html') 

def save_doctor_data(request):

    do_name = request.POST['do_name']
    do_phone = request.POST['do_phone']
    do_specialization = request.POST['do_specialization']
    do_experience = request.POST['do_experience']
    do_email = request.POST['do_email']
    do_password = request.POST['do_password']

    # 🔹 GET IMAGE FILE
    do_img = request.FILES.get('do_img')

    # ---------- PHONE VALIDATION ----------
    phone_pattern = r'^[6789]\d{9}$'
    if not re.match(phone_pattern, do_phone):
        messages.error(request, "Phone number must be 10 digits and start with 6, 7, 8, or 9")
        return redirect('add_doctor')

    # ---------- EMAIL FORMAT VALIDATION ----------
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_pattern, do_email):
        messages.error(request, "Invalid email format!")
        return redirect('add_doctor')

    # ---------- EMAIL DUPLICATE CHECK ----------
    existing_email = models.Doctor.objects.filter(doctor_email=do_email).first()
    if existing_email:
        messages.error(request, "Email already exists!")
        return redirect('add_doctor')

    # ---------- IMAGE VALIDATION ----------
    if not do_img:
        messages.error(request, "Please select a doctor image.")
        return redirect('add_doctor')

    # ---------- SAVE IMAGE MANUALLY ----------
    image_name = do_img.name
    image_path = os.path.join('doctor_uploads', image_name)

    full_path = os.path.join(settings.MEDIA_ROOT, image_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, 'wb+') as destination:
        for chunk in do_img.chunks():
            destination.write(chunk)

    # ---------- SAVE DOCTOR DATA ----------
    sdata = models.Doctor(
        doctor_name=do_name,
        doctor_phone=do_phone,
        doctor_img=image_path,              
        specialization=do_specialization,
        experience=do_experience,
        doctor_email=do_email,
        password=do_password
    )
    sdata.save()

    # ---------- SAVE LOGIN DATA ----------
    udata = models.Login(
        user_name=do_email,
        password=do_password,
        user_type="doctor",
        status="active"
    )
    udata.save()

    messages.success(request, "Doctor added successfully!")
    return redirect('add_doctor')


def view_doctor(request):

    doctor_data=models.Doctor.objects.all()
    context={
        'dlist':doctor_data
    }
    return render(request,'admin/view_doctor.html',context)


def edit_doctor(request,do_id):
    do_data=models.Doctor.objects.get(doctor_id=do_id)
    context={'dlist':do_data
    }
    return render(request, 'admin/edit_doctor.html',context)

def update_doctor(request):
    if request.method == "POST":

        do_id = request.POST['do_id']
        do_name = request.POST['do_name']
        do_phone = request.POST['do_phone']
        do_specialization = request.POST['do_specialization']
        do_experience = request.POST['do_experience']
        do_email = request.POST['do_email']

        d_data = models.Doctor.objects.get(doctor_id=do_id)

        # Phone validation
        phone_pattern = r'^[6789]\d{9}$'
        if not re.match(phone_pattern, do_phone):
            messages.error(request, "Phone number must be 10 digits and start with 6,7,8 or 9")
            return redirect('view_doctor')

        # Email validation
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, do_email):
            messages.error(request, "Invalid email format!")
            return redirect('view_doctor')

        # Email uniqueness check
        existing_email = models.Doctor.objects.filter(
            doctor_email=do_email
        ).exclude(doctor_id=do_id).first()

        if existing_email:
            messages.error(request, "Email already exists!")
            return redirect('view_doctor')

        # UPDATE (IMPORTANT FIXES HERE)
        d_data.doctor_name = do_name
        d_data.doctor_phone = do_phone   # 🔥 VERY IMPORTANT
        d_data.specialization = do_specialization
        d_data.experience = do_experience
        d_data.doctor_email = do_email

        d_data.save()

        messages.success(request, "Doctor profile updated successfully!")
        return redirect('view_doctor')

  

def delete_doctor(request,do_id):
    d_data=models.Doctor.objects.get(doctor_id=do_id)
    d_data.delete()

    return redirect('view_doctor')



def view_feedback(request):

    feedback=models.Feedback.objects.raw("select * from feedback f join patient p on p.patient_id=f.fk_patient_id")
    context={
        'flist':feedback
    }
    return render(request,'admin/viewfeedback.html',context)



def change_password_page(request):
    return render(request, 'admin/admin_change_pass.html')
     
def admin_update_pass(request):
    oldpass=request.POST['o_pass']
    newpass=request.POST['n_pass']
    confirmpass=request.POST['c_pass']
    p_email=request.session['semail']
    pdata=models.Login.objects.get(user_name=p_email) #select * from login where username=value and password=value
    
    if pdata.password != oldpass:
            messages.success(request,'old password is wrong!!!')
            return redirect('change_password_page')

        
    if newpass==confirmpass:
                pdata.password =confirmpass
                pdata.save()
                messages.success(request,'password updated!!!')
                return redirect('change_password_page')

    else:
                messages.success(request,'new password and confirm password should be same!!!')
                return redirect('change_password_page')
    

def edit_doctor_img(request, pid):
    pdata = models.Doctor.objects.get(doctor_id=pid)

    context = {
        'plist': pdata
    }
    return render(request, 'admin/edit_doctor_img.html', context)


def update_doctor_img(request, pid):

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
    return redirect('view_doctor')

def logout(request):
    request.session.flush()   # clears all session data
    messages.success(request, 'Logged out successfully!')
    return redirect('login')