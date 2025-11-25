from django.urls import path
from .views import MemberView, OCRView, SampleEMRPDF, SampleHISPDF, GeneratePDFView

urlpatterns = [
    path('member/', MemberView.as_view(), name='member-view'),
    path('ocr/', OCRView.as_view(), name='ocr'),
    path('generate-pdf/', GeneratePDFView.as_view(), name='generate-pdf'),
    # to be remove
    path('emr/', SampleEMRPDF.as_view(), name='emr'),
    path('his/', SampleHISPDF.as_view(), name='his'),
]