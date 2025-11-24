from django.urls import path
from .views import MemberView, GetMemberTranscations, OCRView

urlpatterns = [
    path('member/', MemberView.as_view(), name='member-view'),
    path('transactions/<str:ph_id>/', GetMemberTranscations.as_view(), name='member-transactions'),
    path('ocr/', OCRView.as_view(), name='ocr'),
]