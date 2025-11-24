from django.db import models

class Patient(models.Model):
    ph_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    gender_choices = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=gender_choices)


class Facility(models.Model):
    name = models.CharField(max_length=50)


class Physician(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='providers')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    license_no = models.CharField(max_length=50, blank=True, null=True)


class MedicalTransactions(models.Model):
    date = models.DateField(auto_now_add=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    provider = models.ForeignKey(Physician, on_delete=models.CASCADE)
    statement_date = models.DateField(blank=True, null=True)
    room_choices = [
        ('pub', 'Public'),
        ('pri', 'Private')
    ]
    room_type = models.CharField(max_length=3, choices=room_choices)
    professional_fee = models.CharField(max_length=50, blank=True, null=True)
    medicines = models.CharField(max_length=50, blank=True, null=True)
    laboratory = models.CharField(max_length=50, blank=True, null=True)
