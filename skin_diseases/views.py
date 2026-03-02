from django.shortcuts import render,redirect
from . import models
from django.contrib import messages
import re
from django.contrib.auth.hashers import make_password
import random
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail






def home(request):
    return render(request,'home/index.html')

def login(request):
    return render(request,'home/login.html')


def check_login(request):
    uname = request.POST.get('username')
    password = request.POST.get('password')

    udata = models.Login.objects.filter(user_name=uname, password=password)
    
    if udata.exists():
        info = udata.first()
        if info.user_type == 'admin':
            request.session['semail'] = info.user_name
            request.session['usertype'] = info.user_type
            return redirect('../administrator/adminlogin')
        elif info.user_type == 'patient':
            request.session['semail'] = info.user_name
            request.session['usertype'] = info.user_type
            # Fetch patient name for better UX
            try:
                patient = models.Patient.objects.get(patient_email=info.user_name)
                request.session['patient_name'] = patient.patient_name
            except models.Patient.DoesNotExist:
                request.session['patient_name'] = "Patient"
            return redirect('../patient/patient_dashboard')
        elif info.user_type == 'doctor':
            request.session['semail'] = info.user_name
            request.session['usertype'] = info.user_type
            # Fetch doctor name for better UX
            try:
                doctor = models.Doctor.objects.get(doctor_email=info.user_name)
                request.session['doctor_name'] = doctor.doctor_name
            except models.Doctor.DoesNotExist:
                request.session['doctor_name'] = "Doctor"
            return redirect('../doctor/doctor_dashboard')
        else:
            messages.error(request, 'Invalid user type')
            return redirect('login')
    else:
        messages.error(request, 'invalid username or password')
        return redirect('login') 

def registration(request):
    return render(request, 'home/registration.html')


def p_reg_savedata(request):

    if request.method == "POST":

        p_name = request.POST.get('patient_name')
        p_phone = request.POST.get('patient_phone')
        p_address = request.POST.get('patient_address')
        p_email = request.POST.get('patient_email')
        p_gender = request.POST.get('patient_gender')
        p_dob = request.POST.get('patient_dob')
        p_password = request.POST.get('password')

        # ---------- PHONE VALIDATION ----------
        phone_pattern = r'^[789]\d{9}$'
        if not re.match(phone_pattern, p_phone):
            messages.error(request, "Phone number must be 10 digits and start with 7, 8, or 9")
            return redirect('registration')

        # ---------- EMAIL FORMAT VALIDATION ----------
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, p_email):
            messages.error(request, "Invalid email format!")
            return redirect('registration')

        # ---------- EMAIL ALREADY EXISTS CHECK ----------
        if models.Patient.objects.filter(patient_email__iexact=p_email).exists():
            messages.error(request, "Email already exists!")
            return redirect('registration')

        # ---------- SAVE PATIENT DATA ----------
        sdata = models.Patient(
            patient_name=p_name,
            patient_phone=p_phone,
            patient_address=p_address,
            patient_email=p_email,
            patient_gender=p_gender,
            patient_dob=p_dob
        )
        sdata.save()

        # ---------- SAVE LOGIN DATA ----------
        udata = models.Login(
            user_name=p_email,
            password=p_password,   # ⚠️ plain text (see note below)
            user_type="patient",
            status="active"
        )
        udata.save()

        messages.success(request, "Registration successful! Please login.")
        return redirect('login')



def forgotpass(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = models.Login.objects.get(user_name=email)

            otp = random.randint(100000, 999999)

            # store in session
            request.session['semail'] = email
            request.session['otp'] = otp

            # send email
            send_mail(
                subject='Your OTP for Password Reset',
                message=f'Your OTP is {otp}. Do not share it with anyone.',
                from_email='projects2faith@gmail.com',
                recipient_list=[email],
                fail_silently=False,
            )

            return redirect('OTPpage')

        except models.Login.DoesNotExist:
            messages.error(request, 'Email not registered!')
            return redirect('forgotpass')

    return render(request, 'home/forgotpass.html')




def OTPpage(request):
    if 'semail' not in request.session:
        return redirect('forgotpass')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')

        if entered_otp == str(session_otp):
            # OTP correct → remove otp from session
            del request.session['otp']
            return redirect('newpassword')
        else:
            messages.error(request, 'Invalid OTP!')
            return redirect('OTPpage')

    return render(request, 'home/OTPpage.html')



def newpassword(request):
    if 'semail' not in request.session:
        return redirect('forgotpass')

    return render(request, 'home/newpassword.html')






def update_forgot_pass(request):
    if request.method == 'POST':

        if 'semail' not in request.session:
            messages.error(request, 'Session expired. Try again.')
            return redirect('forgotpass')

        newpass = request.POST.get('new_pass')
        confirmpass = request.POST.get('confirm_pass')
        email = request.session.get('semail')

        if newpass != confirmpass:
            messages.error(request, 'Passwords do not match!')
            return redirect('newpassword')

        try:
            user = models.Login.objects.get(user_name=email)
            user.password = newpass
            user.save()

            # clear session
            request.session.flush()

            messages.success(request, 'Password updated successfully!')
            return redirect('login')

        except models.Login.DoesNotExist:
            messages.error(request, 'User does not exist!')
            return redirect('forgotpass')
