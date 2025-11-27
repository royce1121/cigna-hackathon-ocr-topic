from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.generic import DetailView, ListView
from .models import Patient, MedicalTransactions
from .controller import PDFController
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from io import BytesIO
from django.core.files.base import ContentFile
import pymupdf
import io
import json
from django.http import FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import os
import pymupdf
from fillpdf import fillpdfs
import fitz
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

TMP_DIR = "tmp"
os.makedirs(TMP_DIR, exist_ok=True)  # ensure temp folder exists

class MemberView(View):
    template_name = 'member/landing_page.html'

    def get(self, request):
        ph_id = request.GET.get("philhealth_id")
        patient = None
        transactions = None
        if ph_id:
            patient = Patient.objects.filter(ph_id=ph_id)
            if patient:
                patient = patient.first()
                transactions = MedicalTransactions.objects.filter(
                    patient=patient
                ).order_by('date')
        return render(request, self.template_name, {
            'ph_id': ph_id,
            'patient': patient,
            'transactions': transactions
        })
    

class OCRView(View):
    def post(self, request):
        trans_id = request.POST.get("patient_id")
        text_result = []
        member_transaction = MedicalTransactions.objects.get(id=int(trans_id))
        if member_transaction.emr_file:
            pdf_controller = PDFController(pdf_file=member_transaction.emr_file)
            pdf_controller.get_pdf_text()
            text_result = pdf_controller.text_result
        return JsonResponse({"text_result": text_result})
    

class GeneratePDFView(View):
    def get_forms(self):
        form_path = 'healthcare_form_assistant/health_form/cf1.pdf'
        return form_path

    def post(self, request):
        doc = pymupdf.open(self.get_forms())
        page = doc[0]

        # to be adjusted, this is hardcoded but we needed to map this using AI
        label_value_map = {
            "PhilHealth Identification Number (PIN) of Member:": "012345678912",
            "Last Name": "SAMPLE",
            "First Name": "SAMPLE",
            "Name Extension": "SAMPLE",
            "Middle Name": "SAMPLE",
            "Unit/Room No./Floor": "SAMPLE",
            "Building Name": "SAMPLE",
            "Lot/Blk/House/Bldg.No": "SAMPLE",
            "Street": "SAMPLE",
            "Subdivision/Village": "SAMPLE",
            "Barangay": "SAMPLE",
            "City/Municipality": "SAMPLE",
            "Province": "SAMPLE",
            "Country": "SAMPLE",
            "Zip Code": "SAMPLE",
            "Landline No. (Area Code + Tel. No.)": "SAMPLE",
            "Mobile No.": "SAMPLE",
            "Email Address": "SAMPLE",
        }
        for label, value in label_value_map.items():
            text_instances = page.search_for(label)
            if text_instances:
                rect = text_instances[0]
                x = rect.x1 - 50
                y = rect.y0 - 5
                page.insert_text((x, y), value, fontsize=10)

        pdf_bytes = io.BytesIO()
        doc.save(pdf_bytes)
        pdf_bytes.seek(0)
        doc.close()

        # Return file
        return FileResponse(pdf_bytes, as_attachment=True, filename="sample_cf1.pdf")


@method_decorator(csrf_exempt, name='dispatch')
class GenerateFormsPDFView(View):
    def get_cf_fields(self, cf_no):
        file_path = self.get_cf_form(cf_no)
        if cf_no in ['1', '2']:
            print(fillpdfs.get_form_fields(file_path))
            print(cf_no)
        return list(fillpdfs.get_form_fields(file_path))

    def get_cf_form(self, cf_no):
        return 'healthcare_form_assistant/health_form/cf{}.pdf'.format(cf_no)
    
    def get_transaction_data(self, transaction_id):
        return MedicalTransactions.objects.get(id=transaction_id)

    def prepare_cf_data(self, transaction_data, data, cf_no):
        if cf_no == '1':
            return self.prepare_cf1_data(transaction_data)
        if cf_no == '2':
            return self.prepare_cf2_data(transaction_data, data)
        elif cf_no == '3':
            return self.prepare_cf3_data(transaction_data, data, cf_no)

    def prepare_cf1_data(self, transaction_data):
        patient = transaction_data.patient
        philhealth_id = patient.ph_id
        first_part_id = philhealth_id[0:2]
        second_part_id = philhealth_id[2:11]
        last_part_id = philhealth_id[11]
        patient_lastname = patient.last_name
        patient_firstname = patient.first_name
        patient_extensions = ''
        patient_middlename = patient.middle_name
        form_fields = self.get_cf_fields("1")
        data_dict = {
            form_fields[0] : first_part_id,
            form_fields[1] : second_part_id,
            form_fields[2] : last_part_id,
            form_fields[3] : patient_lastname,
            form_fields[4] : patient_firstname,
            form_fields[5] : patient_extensions,
            form_fields[6] : patient_middlename,
            form_fields[7] : patient.birth_date.strftime("%m"),
            form_fields[8] : patient.birth_date.strftime("%d"),
            form_fields[9] : patient.birth_date.year,
            # skip 10 and 11
            form_fields[12] : patient.unit_room_no_floor,
            form_fields[13] : patient.building_name,
            form_fields[14] : patient.lot_blk_house_bldg_no,
            form_fields[15] : patient.street,
            form_fields[16] : patient.subdivision_village,
            form_fields[17] : patient.barangay,
            form_fields[18] : patient.city_municipality,
            form_fields[19] : patient.province,
            form_fields[20] : patient.country,
            form_fields[21] : patient.zip_code,
            form_fields[22] : patient.landline_no,
            form_fields[23] : patient.mobile_no,
            form_fields[24] : patient.email_address
        }
        if patient.gender == 'M':
            gender_index = 10
        else:
            gender_index = 11
        data_dict[form_fields[gender_index]] = 'Yes_hykr'
        return data_dict

    def prepare_cf2_data(self, transaction_data, cf2_data):
        accreditation_number = "123456789"
        medical_institution = "General Doctors Hospital"
        address_buildingST = "123 St."
        address_city = "Manila"
        address_province = " Manila"

        #Part 2: PATIENT CONFINEMENT INFORMATION
        patient = transaction_data.patient
        patient_lastname = patient.last_name
        patient_firstname = patient.first_name
        patient_extensions = ''
        patient_middlename = patient.middle_name
        form_fields = self.get_cf_fields("2")
        data_dict = {
            form_fields[0] : accreditation_number,
            form_fields[1] : medical_institution,
            form_fields[2] : address_buildingST,
            form_fields[3] : address_city,
            form_fields[4] : address_province,
            form_fields[5] : patient_lastname,
            form_fields[6] : patient_firstname,
            form_fields[7] : patient_extensions,
            form_fields[8] : patient_middlename,
            form_fields[9] : "Yes_oaef", # hardcoded for now
        }
        starting_count = 16
        check_box_field = [21, 28]
        disposition_box = {
            "Improved": 30,
            "Recovered": 31,
            "Discharge": 32,
            "Absconded": 33
        }
        for label, value in cf2_data.items():
            if label == 'discharge_diagnosis':
                for diag_dict in value:
                    for key, dict_val in diag_dict.items():
                        data_dict[form_fields[starting_count]] = dict_val
                        starting_count += 1
            else:
                if starting_count in check_box_field:
                    field_checker = starting_count
                    index = 0
                    value_dict = {
                        21: ['Yes_qklh', 'Yes_yxbo'],
                        28: ['Yes_jpcv', 'Yes_hrdk'],
                    }
                    if value == 'pm':
                        index += 1
                        field_checker += 1
                    yes_value = value_dict[starting_count][index]
                    data_dict[form_fields[field_checker]] = yes_value
                    starting_count += 1
                elif starting_count == 30:
                    data_dict[form_fields[disposition_box[value]]] = 'Yes_oaef'
                    starting_count += 3
                elif starting_count == 34:
                    field_value = starting_count
                    if value != 'Private':
                        field_value += 1
                    data_dict[form_fields[field_value]] = 'Yes_oaef'
                    starting_count += 1
                else:
                    data_dict[form_fields[starting_count]] = value
                starting_count += 1
        return data_dict

    def prepare_cf3_data(self, transaction_data, data, cf_no):
        accreditation_number = "123456789"

        #Part 2: PATIENT CONFINEMENT INFORMATION
        patient = transaction_data.patient
        patient_lastname = patient.last_name
        patient_firstname = patient.first_name
        patient_middlename = patient.middle_name
        form_fields = self.get_cf_fields(cf_no)
        data_dict = {
            form_fields[0] : accreditation_number,
            form_fields[1] : patient_lastname,
            form_fields[2] : patient_firstname,
            form_fields[3] : patient_middlename,
            form_fields[4] : data["Chief Complaint / Reason for Admission"],
            form_fields[5] : data["date_admitted_month"],
            form_fields[6] : data["date_admitted_day"],
            form_fields[7] : data["date_admitted_year"],
            form_fields[10] : data["date_discharge_month"],
            form_fields[11] : data["date_discharge_day"],
            form_fields[12] : data["date_discharge_year"],
            form_fields[15]: data["Brief History of Present Illness / OB History"],
            form_fields[16] : data["BP"],
            form_fields[17] : data["CR"],
            form_fields[18]: data["RR"],
            form_fields[19]: data["Temperature"],
            form_fields[20] : data["Abdomen"],
            form_fields[21]: data["GU"],
            form_fields[22]: data["Chest/Lungs"],
            form_fields[24] : data["Skin/Extremities"],
            form_fields[25] : data["CVS"],
            form_fields[26]: data["Neuro Examination"],
            form_fields[27]: data["Course in the Wards"],
            form_fields[28]: data["Pertinent Laboratory and Diagnostic Findings"]
        }
        if data['date_admitted_am_or_pm'] == "am":
            data_dict[form_fields[8]] = data["date_admitted_time"]
        elif data['date_admitted_am_or_pm'] == "pm":
            data_dict[form_fields[9]] = data["date_admitted_time"]
        if data['date_discharge_am_or_pm'] == "am":
            data_dict[form_fields[13]] = data["date_discharge_time"]
        elif data['date_discharge_am_or_pm'] == "pm":
            data_dict[form_fields[14]] = data["date_discharge_time"]
        return data_dict

    def create_pdf(self, transaction_data, data, cf_no):
        tmp_path = os.path.join(TMP_DIR, "cf{}_temp.pdf".format(cf_no))
        data_dict = self.prepare_cf_data(transaction_data, data, cf_no)
        fillpdfs.write_fillable_pdf(
            input_pdf_path=self.get_cf_form(cf_no),
            output_pdf_path=tmp_path,  # write directly to BytesIO
            data_dict=data_dict
        )
        pdf_bytes = BytesIO(open(tmp_path, "rb").read())
        os.remove(tmp_path)
        cf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        return cf_doc

    def post(self, request):
        data = json.loads(request.body)
        transaction_data = self.get_transaction_data(data.get('transaction_id'))
        json_data = data.get('json_data')
        cf2_data = json_data.get('CF2')
        cf1_doc = self.create_pdf(transaction_data, cf2_data, '1')
        cf2_doc = self.create_pdf(transaction_data, cf2_data, '2')
        for page in cf2_doc:
            cf1_doc.insert_pdf(cf2_doc, from_page=page.number, to_page=page.number)
        cf3_data = json_data.get('CF3')
        cf3_doc = self.create_pdf(transaction_data, cf3_data, '3')
        for page in cf3_doc:
            cf1_doc.insert_pdf(cf3_doc, from_page=page.number, to_page=page.number)
        final_bytes = io.BytesIO()
        cf1_doc.save(final_bytes)
        final_bytes.seek(0)
        cf1_doc.close()
        cf2_doc.close()
        cf3_doc.close()
        return HttpResponse(final_bytes, content_type='application/pdf')


class GenerateHospitalBillView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        patient = MedicalTransactions.objects.get(id=int(data.get('transaction_id'))).patient
        json_data = data.get('json_data')
        billing = json_data.get('billing')
        cf_2 = json_data.get('CF2')
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Draw page border
        border_margin = 30
        c.setLineWidth(2)
        c.rect(border_margin, border_margin, width - 2*border_margin, height - 2*border_margin)

        # Title
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width/2, height - 60, "Hospital Billing Statement")

        # Draw Patient Information section with shading
        patient_y_start = height - 100
        c.setFillColorRGB(0.9, 0.9, 0.9)  # light gray background
        c.rect(45, patient_y_start - 5, 500, 60, fill=1, stroke=0)

        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, patient_y_start, "Patient Information")
        c.setFont("Helvetica", 10)
        c.drawString(50, patient_y_start - 20, "First Name: {}".format(patient.first_name))
        c.drawString(50, patient_y_start - 35, "Last Name: {}".format(patient.last_name))
        c.drawString(50, patient_y_start - 50, "RVS Code: {}".format(cf_2['discharge_diagnosis'][0]['rvs']))

        # Charges section with header shading
        charges_y_start = patient_y_start - 90
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.rect(45, charges_y_start - 5, 500, 25, fill=1, stroke=0)

        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, charges_y_start, "Charges")

        # Charges rows
        c.setFont("Helvetica", 10)
        charges = [
            ("Professional Fee", billing['professional']),
            ("Hospital Fee", billing['hospital']),
            ("Procedure Fee", billing['procedure']),
            ("Medicine/Pharmacy Fee", billing['medicine']),
            ("Subtotal", billing['total']),
            ("PhilHealth Deduction", ""),
            ("Total Amount Due", "")
        ]
        line_spacing = 20
        start_y = charges_y_start - 20

        for i, label in enumerate(charges):
            y = start_y - i * line_spacing
            c.drawString(50, y, "{}: {}".format(label[0], label[1]))
            c.line(45, y - 5, 545, y - 5)

        c.setFont("Helvetica-Oblique", 9)

        c.save()
        buffer.seek(0)

        return HttpResponse(buffer.getvalue(), content_type='application/pdf')


class DesignedBlankHospitalBillView(View):
    def get(self, request, *args, **kwargs):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Draw page border
        border_margin = 30
        c.setLineWidth(2)
        c.rect(border_margin, border_margin, width - 2*border_margin, height - 2*border_margin)

        # Title
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width/2, height - 60, "Hospital Billing Statement")

        # Draw Patient Information section with shading
        patient_y_start = height - 100
        c.setFillColorRGB(0.9, 0.9, 0.9)  # light gray background
        c.rect(45, patient_y_start - 5, 500, 60, fill=1, stroke=0)

        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, patient_y_start, "Patient Information")
        c.setFont("Helvetica", 10)
        c.drawString(50, patient_y_start - 20, "First Name: ____________________")
        c.drawString(50, patient_y_start - 35, "Last Name: ____________________")
        c.drawString(50, patient_y_start - 50, "Diagnosis Code: _______________")

        # Charges section with header shading
        charges_y_start = patient_y_start - 90
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.rect(45, charges_y_start - 5, 500, 25, fill=1, stroke=0)

        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, charges_y_start, "Charges")

        # Charges rows
        c.setFont("Helvetica", 10)
        charges = [
            "Professional Fee",
            "Hospital Fee",
            "Procedure Fee",
            "Medicine/Pharmacy Fee",
            "Subtotal",
            "PhilHealth Deduction",
            "Total Amount Due"
        ]
        line_spacing = 20
        start_y = charges_y_start - 20

        for i, label in enumerate(charges):
            y = start_y - i * line_spacing
            c.drawString(50, y, f"{label}: ____________________")
            # Optional: draw line for alignment
            c.line(45, y - 5, 545, y - 5)

        # Footer note
        c.setFont("Helvetica-Oblique", 9)

        c.save()
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="sample_hospital_bill.pdf"'
        return response

# to be remove, this is just put for PDF Generation for testing
class SampleEMRPDF(View):
    def get(self, request, *args, **kwargs):
        buffer = BytesIO()
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40
        )

        story = []

        # Title
        story.append(Paragraph("<b>Electronic Medical Record (EMR) - Sample</b>", styles["Title"]))
        story.append(Spacer(1, 12))

        # Patient Information
        patient_info = [
            ["Name:", "Juan Dela Cruz"],
            ["Age:", "45"],
            ["Sex:", "Male"],
            ["PhilHealth No.:", "12-345678901-2"],
            ["Accommodation:", "Private"],
            ["Admission Date & Time:", "2025-11-27 09:00"],
            ["Discharge Date & Time:", "2025-11-30 15:00"],
            ["Patient Disposition:", "Recovered"],
            ["Admission Diagnosis:", "Acute Febrile Illness"]
        ]
        t_patient = Table(patient_info, colWidths=[160, 260])
        t_patient.setStyle(TableStyle([
            ("ALIGN", (0,0), (-1,-1), "LEFT"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
            ("FONTSIZE", (0,0), (-1,-1), 10),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ]))
        story.append(Paragraph("<b>Patient Information</b>", styles["Heading2"]))
        story.append(t_patient)
        story.append(Spacer(1, 12))

        # Vital Signs
        vital_signs = [
            ["BP:", "130/90 mmHg"],
            ["Heart Rate:", "89 bpm"],
            ["Respiration Rate:", "20 cpm"],
            ["Temperature:", "37.8 C"]
        ]
        t_vital = Table(vital_signs, colWidths=[120, 300])
        t_vital.setStyle(TableStyle([
            ("ALIGN", (0,0), (-1,-1), "LEFT"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
            ("FONTSIZE", (0,0), (-1,-1), 10),
        ]))
        story.append(Paragraph("<b>Vital Signs</b>", styles["Heading2"]))
        story.append(t_vital)
        story.append(Spacer(1, 12))

        # Chief Complaint & Diagnosis
        story.append(Paragraph("<b>Chief Complaint:</b> High-grade fever for 3 days", styles["Normal"]))
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>Diagnosis:</b> Acute Febrile Illness", styles["Normal"]))
        story.append(Spacer(1, 12))
        # Discharge Diagnosis as sentence
        discharge_text = """
        <b>Discharge Diagnosis / Procedure:</b> Debridement of Nail(s) by any method(s) — one to five nails (RVS Code: 11720).  
        Procedure date: 2025‑11‑29.  
        Patient outcome: Recovered. No complications reported.
        """
        story.append(Paragraph(discharge_text, styles["Normal"]))
        story.append(Spacer(1, 12))
        # Billing Section
        billing_data = [
            ["Professional Fee", "₱ 2,000.00"],
            ["Lab Fee", "₱ 1,500.00"],
            ["Procedure Fee", "₱ 1,200.00"],
            ["Medicine Fee", "₱ 800.00"],
            ["Total Billing Price", "₱ 5,500.00"]
        ]
        t_billing = Table(billing_data, colWidths=[200, 150])
        t_billing.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("ALIGN", (1,0), (1,-1), "RIGHT"),
            ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
            ("FONTSIZE", (0,0), (-1,-1), 10),
            ("BACKGROUND", (0,-1), (-1,-1), colors.lightgrey),
        ]))
        story.append(Paragraph("<b>Billing Information</b>", styles["Heading2"]))
        story.append(t_billing)
        story.append(Spacer(1, 12))

        # Build PDF
        doc.build(story)

        pdf = buffer.getvalue()
        buffer.close()

        # Optionally save PDF to model
        record = MedicalTransactions.objects.get(id=1)
        if not record.emr_file:
            record.emr_file.save("SAMPLE_EMR.pdf", ContentFile(pdf))
            record.save()

        # Return PDF as download
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="sample_emr.pdf"'
        return response


class SampleEMRPDF2(View):
    def get(self, request, *args, **kwargs):
        buffer = BytesIO()
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40
        )

        story = []

        # Title
        story.append(Paragraph("<b>Electronic Medical Record (EMR) - Sample 2</b>", styles["Title"]))
        story.append(Spacer(1, 12))

        # Patient Information
        patient_info = [
            ["Name:", "John Doe"],
            ["Age:", "30"],
            ["Sex:", "Male"],
            ["PhilHealth No.:", "22-987654321-0"],
            ["Accommodation:", "Ward"],
            ["Admission Date & Time:", "2025-10-12 14:30"],
            ["Discharge Date & Time:", "2025-10-15 10:45"],
            ["Patient Disposition:", "Improved"],
            ["Admission Diagnosis:", "Acute Gastroenteritis"]
        ]
        t_patient = Table(patient_info, colWidths=[160, 260])
        t_patient.setStyle(TableStyle([
            ("ALIGN", (0,0), (-1,-1), "LEFT"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
            ("FONTSIZE", (0,0), (-1,-1), 10),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ]))
        story.append(Paragraph("<b>Patient Information</b>", styles["Heading2"]))
        story.append(t_patient)
        story.append(Spacer(1, 12))

        # Vital Signs
        vital_signs = [
            ["BP:", "110/70 mmHg"],
            ["Heart Rate:", "92 bpm"],
            ["Respiration Rate:", "21 cpm"],
            ["Temperature:", "38.2 C"]
        ]
        t_vital = Table(vital_signs, colWidths=[120, 300])
        t_vital.setStyle(TableStyle([
            ("ALIGN", (0,0), (-1,-1), "LEFT"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
            ("FONTSIZE", (0,0), (-1,-1), 10),
        ]))
        story.append(Paragraph("<b>Vital Signs</b>", styles["Heading2"]))
        story.append(t_vital)
        story.append(Spacer(1, 12))

        # Chief Complaint & Diagnosis
        story.append(Paragraph("<b>Chief Complaint:</b> Abdominal pain and vomiting", styles["Normal"]))
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>Diagnosis:</b> Acute Gastroenteritis", styles["Normal"]))
        story.append(Spacer(1, 12))

        # Discharge Diagnosis with New RVS
        discharge_text = """
        <b>Discharge Diagnosis / Procedure:</b> Intravenous hydration therapy (RVS Code: 99283).  
        Procedure date: 2025-10-13.  
        Patient outcome: Improved condition upon discharge. No adverse reactions.
        """
        story.append(Paragraph(discharge_text, styles["Normal"]))
        story.append(Spacer(1, 12))

        # Billing Section
        billing_data = [
            ["Professional Fee", "₱ 1,800.00"],
            ["Lab Tests", "₱ 900.00"],
            ["IV Fluids & Supplies", "₱ 750.00"],
            ["Room & Board", "₱ 1,200.00"],
            ["Total Billing Price", "₱ 4,650.00"]
        ]
        t_billing = Table(billing_data, colWidths=[200, 150])
        t_billing.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("ALIGN", (1,0), (1,-1), "RIGHT"),
            ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
            ("FONTSIZE", (0,0), (-1,-1), 10),
            ("BACKGROUND", (0,-1), (-1,-1), colors.lightgrey),
        ]))
        story.append(Paragraph("<b>Billing Information</b>", styles["Heading2"]))
        story.append(t_billing)
        story.append(Spacer(1, 12))

        # Build PDF
        doc.build(story)

        pdf = buffer.getvalue()
        buffer.close()

        # Optional save to model
        record = MedicalTransactions.objects.get(id=2)
        if not record.emr_file:
            record.emr_file.save("SAMPLE_EMR_2.pdf", ContentFile(pdf))
            record.save()

        # Return PDF to browser
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="sample_emr_2.pdf"'
        return response