from django.shortcuts import render
from django.http import HttpResponse
from django.views import View


class MemberView(View):
    template_name = 'member/landing_page.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        philhealth_id = request.POST.get("philhealth_id")

        user_info = {
            "philhealth_id": philhealth_id,
            "name": "Juan Dela Cruz",
            "status": "Active Member",
            "birthdate": "1992-09-12",
        }

        return render(request, self.template_name, {"user_info": user_info})