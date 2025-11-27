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
    unit_room_no_floor = models.CharField("Unit/Room No./Floor", max_length=255, blank=True, null=True)
    building_name = models.CharField("Building Name", max_length=255, blank=True, null=True)
    lot_blk_house_bldg_no = models.CharField("Lot/Blk/House/Bldg.No", max_length=255, blank=True, null=True)
    street = models.CharField("Street", max_length=255, blank=True, null=True)
    subdivision_village = models.CharField("Subdivision/Village", max_length=255, blank=True, null=True)
    barangay = models.CharField("Barangay", max_length=255, blank=True, null=True)
    city_municipality = models.CharField("City/Municipality", max_length=255, blank=True, null=True)
    province = models.CharField("Province", max_length=255, blank=True, null=True)
    country = models.CharField("Country", max_length=255, blank=True, null=True)
    zip_code = models.CharField("Zip Code", max_length=20, blank=True, null=True)
    landline_no = models.CharField("Landline No. (Area Code + Tel. No.)", max_length=50, blank=True, null=True)
    mobile_no = models.CharField("Mobile No.", max_length=50, blank=True, null=True)
    email_address = models.EmailField("Email Address", blank=True, null=True)

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