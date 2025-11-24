from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views import View
from django.views.generic import DetailView, ListView
from .models import Patient, MedicalTransactions
from paddleocr import PaddleOCR
import os
import fitz

ocr = PaddleOCR(lang='en')
class MemberView(View):
    template_name = 'member/landing_page.html'

    def get(self, request):
        ph_id = request.GET.get("philhealth_id")
        patient = None
        if ph_id:
            patient = Patient.objects.filter(ph_id=ph_id)
            if patient:
                patient = patient.first()
        return render(request, self.template_name, {'ph_id': ph_id, 'patient': patient})
    

class GetMemberTranscations(ListView):
    model = MedicalTransactions
    template_name = 'member/transaction_table.html'
    context_object_name = "transactions"

    def get_queryset(self):
        ph_id = self.kwargs.get("ph_id")
        patient = get_object_or_404(Patient, ph_id=ph_id)
        return MedicalTransactions.objects.filter(
            patient=patient
        ).order_by('date')


class OCRView(View):
    template_name = "member/ocr_reader.html"

    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        selected_file = request.FILES.get("file")
        text_result = []

        if selected_file:
            temp_dir = "temp_files"
            file_path = os.path.join(temp_dir, selected_file.name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "wb+") as f:
                for chunk in selected_file.chunks():
                    f.write(chunk)
            
            # OCR Process
            transform_pdf = fitz.open(file_path)
            for page_number, page in enumerate(transform_pdf):
                print('=============')
                page_text = page.get_text("text").strip()
                if page_text:
                    print(page_text)
                print('=======================')
                pix = page.get_pixmap()
                img_path = os.path.join(temp_dir, f"{selected_file.name}_page_{page_number}.png")
                pix.save(img_path)
                try:
                    result = ocr.predict(img_path)
                    print(result)
                    print('111111111111111111111111111111')
                    for page_result in result:
                        rec_texts = page_result.get('rec_texts', [])
                        text_result.extend(rec_texts)
                except Exception as e:
                    text_result.append(f"Error processing page {page_number}: {e}")
        print('================')
        print(text_result)
        print('=====================')
        return render(request, self.template_name, {"text_result": text_result})