from django.urls import path
from .views import (MemberView, OCRView, SampleEMRPDF, SampleEMRPDF2,
GeneratePDFView, GenerateFormsPDFView, DesignedBlankHospitalBillView, GenerateHospitalBillView
)
urlpatterns = [
    path('member/', MemberView.as_view(), name='member-view'),
    path('ocr/', OCRView.as_view(), name='ocr'),
    path('generate-pdf/', GeneratePDFView.as_view(), name='generate-pdf'),
    path('generate-cf3/', GenerateFormsPDFView.as_view(), name='generate_cf3'),
    # to be remove
    path('emr/', SampleEMRPDF.as_view(), name='emr'),
    path('emr_2/', SampleEMRPDF2.as_view(), name='emr_2'),
    path('billing_provider/', DesignedBlankHospitalBillView.as_view(), name='billing'),
    path('generate_billing/', GenerateHospitalBillView.as_view(), name='generate_billing'),
]