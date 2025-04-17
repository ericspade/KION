from django.shortcuts import redirect


def redirect_api(request):
    return redirect('http://localhost:8001/videos/api-fast/view-event')
