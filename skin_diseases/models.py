# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Appointment(models.Model):
    appointment_id = models.AutoField(primary_key=True)
    fk_patient_id = models.IntegerField()
    fk_doctor_id = models.IntegerField()
    appointment_date = models.DateField()
    remarks = models.CharField(max_length=500)
    medical_guidance = models.CharField(max_length=500)

    class Meta:
        managed = False
        db_table = 'appointment'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Disease(models.Model):
    disease_id = models.AutoField(primary_key=True)
    disease_name = models.CharField(max_length=300)
    description = models.CharField(max_length=300)
    symptoms = models.CharField(max_length=300)
    precautions = models.CharField(max_length=300)

    class Meta:
        managed = False
        db_table = 'disease'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Doctor(models.Model):
    doctor_id = models.AutoField(primary_key=True)
    doctor_name = models.CharField(max_length=200)
    doctor_phone = models.IntegerField()
    doctor_img = models.CharField(max_length=300)
    specialization = models.CharField(max_length=300)
    experience = models.CharField(max_length=200)
    doctor_email = models.CharField(max_length=200)
    password = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'doctor'


class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    fk_patient_id = models.IntegerField()
    message = models.CharField(max_length=500)
    submitted_date = models.DateField()

    class Meta:
        managed = False
        db_table = 'feedback'


class Login(models.Model):
    user_name = models.CharField(primary_key=True, max_length=50)
    password = models.CharField(max_length=20)
    user_type = models.CharField(max_length=20)
    status = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'login'


class MedicalGuidence(models.Model):
    guidence_id = models.AutoField(primary_key=True)
    fk_disease_id = models.CharField(max_length=50)
    treatment = models.CharField(max_length=500)
    precuation = models.CharField(max_length=500)
    consult_doctor = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'medical_guidence'


class ModelDetails(models.Model):
    model_id = models.AutoField(primary_key=True)
    model_name = models.CharField(max_length=200)
    accuracy = models.DecimalField(max_digits=5, decimal_places=2)
    loss = models.DecimalField(max_digits=5, decimal_places=2)
    trained_on = models.DateField()
    dataset_used = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'model_details'


class Patient(models.Model):
    patient_id = models.AutoField(primary_key=True)
    patient_name = models.CharField(max_length=200)
    patient_phone = models.CharField(max_length=200)
    patient_address = models.CharField(max_length=200)
    patient_email = models.CharField(max_length=200)
    patient_gender = models.CharField(max_length=200)
    patient_dob = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'patient'


class Predictions(models.Model):
    prediction_id = models.AutoField(primary_key=True)
    fk_skin_image_id = models.CharField(max_length=50)
    fk_disease_id = models.CharField(max_length=50)
    confidance_score = models.CharField(max_length=200)
    predicted_at = models.CharField(max_length=500)
    disease_name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'predictions'


class SkinImages(models.Model):
    skin_image_id = models.AutoField(primary_key=True)
    fk_patient_id = models.IntegerField()
    image_path = models.CharField(max_length=500)
    uploaded_date = models.DateField()

    class Meta:
        managed = False
        db_table = 'skin_images'
