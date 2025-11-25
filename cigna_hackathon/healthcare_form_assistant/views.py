from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
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
from django.http import FileResponse

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
    template_name = "member/ocr_reader.html"

    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        selected_file = request.FILES.get("file")
        text_result = []

        if selected_file:
            pdf_controller = PDFController(pdf_file=selected_file)
            pdf_controller.get_pdf_text()
            text_result = pdf_controller.text_result
        return render(request, self.template_name, {"text_result": text_result})
    

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


# to be remove, this is just put for PDF Generation for testing
class SampleEMRPDF(View):
    def get(self, request, *args, **kwargs):
        buffer = BytesIO()
        styles = getSampleStyleSheet()

        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []

        content = """
            <h1>Electronic Medical Record (EMR) - Sample</h1>
            <b>Patient Information</b><br/>
            Name: Juan Dela Cruz<br/>
            Age: 45<br/>
            Sex: Male<br/>
            PhilHealth No.: 12-345678901-2<br/><br/>

            <b>Vital Signs</b><br/>
            BP: 130/90 mmHg<br/>
            Heart Rate: 89 bpm<br/>
            Resp Rate: 20 cpm<br/>
            Temperature: 37.8 C<br/><br/>

            <b>Chief Complaint:</b><br/>
            High-grade fever for 3 days<br/><br/>

            <b>Diagnosis:</b><br/>
            Acute Febrile Illness (ICD-10: R50.9)<br/><br/>
        """

        story.append(Paragraph(content, styles["Normal"]))
        doc.build(story)

        pdf = buffer.getvalue()
        buffer.close()

        # Save PDF to Django model
        record = MedicalTransactions.objects.get(
            id=3
        )
        if not record.emr_file:
            record.emr_file.save("SAMPLE_EMR.pdf", ContentFile(pdf))
            record.save()

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="sample_emr.pdf"'
        return response


class SampleHISPDF(View):
    def get(self, request, *args, **kwargs):
        buffer = BytesIO()
        styles = getSampleStyleSheet()

        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []

        content = """
            <h1>Hospital Information System (HIS) Record - Sample</h1>

            <b>Admission Details</b><br/>
            Admission No.: ADM-2025-000123<br/>
            Date Admitted: Jan 15, 2025<br/>
            Room: Ward 3B Bed 12<br/><br/>

            <b>Patient Details</b><br/>
            Name: Maria Santos<br/>
            DOB: Feb 25, 1980<br/>
            Sex: Female<br/>
            Address: Quezon City<br/><br/>

            <b>Course in the Ward:</b><br/>
            Patient monitored for suspected pneumonia. Started on IV antibiotics.<br/><br/>

            <b>Final Diagnosis:</b><br/>
            Pneumonia Moderate Risk (ICD-10: J18.9)<br/><br/>

            <b>Attending Physician:</b><br/>
            Dr. Ana Ramirez<br/>
            License No.: 9876543<br/>
        """

        story.append(Paragraph(content, styles["Normal"]))
        doc.build(story)

        pdf = buffer.getvalue()
        buffer.close()
        # Save PDF to Django model
        record = MedicalTransactions.objects.get(
            id=3
        )
        if not record.his_file:
            record.his_file.save("SAMPLE_HIS.pdf", ContentFile(pdf))
            record.save()
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="sample_his.pdf"'
        return response