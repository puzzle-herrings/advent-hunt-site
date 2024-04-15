from django.template.response import TemplateResponse

def home_page(request):
    return TemplateResponse(request, "home.html", {})
