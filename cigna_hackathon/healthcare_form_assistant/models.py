from django.db import models
from datetime import date


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

    def get_fullname(self):
        full_name = '{}, {}'.format(self.last_name, self.first_name)
        if self.middle_name:
            full_name = '{} {}.'.format(full_name, self.middle_name[0])
        return full_name

    def get_age(self):
        today = date.today()
        age = None
        if self.birth_date:
            age = today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return age


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
    emr_file = models.FileField(upload_to='medical_records/', blank=True, null=True)
    his_file = models.FileField(upload_to='medical_records/', blank=True, null=True)

    def get_total_fee(self):
        int_prof_fee = int(self.professional_fee)
        int_medicines = int(self.medicines)
        int_laboratory = int(self.laboratory)
        return int_prof_fee + int_medicines + int_laboratory