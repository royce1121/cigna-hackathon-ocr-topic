from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views import View
from django.views.generic import DetailView, ListView
from .models import Patient, MedicalTransactions

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
    # def get(self, request):
    #     ph_id = request.GET.get("ph_id")
    #     patient = Patient.objects.filter(ph_id=ph_id)
    #     mt_query = None
    #     if patient:
    #         patient = patient.first()
    #         mt_query = MedicalTransactions.objects.filter(
    #             patient=patient
    #         ).order_by('date')
    #     return render(request, self.template_name, {'ph_id': ph_id, 'transactions': mt_query})