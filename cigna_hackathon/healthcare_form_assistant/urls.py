from django.urls import path
from .views import MemberView, GetMemberTranscations

urlpatterns = [
    path('member/', MemberView.as_view(), name='member-view'),
    path('transactions/<str:ph_id>/', GetMemberTranscations.as_view(), name='member-transactions'),
]