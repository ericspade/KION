from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import dedup_request

from django.shortcuts import redirect


def redirect_api(request):
    return redirect('http://localhost:8001/videos/api-fast/view-event')


@dedup_request(timeout=10, persist_days=7)
@csrf_exempt
def api_view_event(request):
    if request.method == "POST":
        return JsonResponse({"status": "queued"}, status=202)
    return JsonResponse({"error": "Invalid method"}, status=405)


def view_event_page(request):
    return render(request, "videos/view_event.html")
