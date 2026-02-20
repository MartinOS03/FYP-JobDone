# REST API endpoints for jobs - used for JSON API calls
# These were from the original React frontend setup, keeping them for API compatibility
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
import json
from .models import Job


# GET all jobs or POST a new job
@csrf_exempt
def job_list(request):
    if request.method == 'GET':
        jobs = list(Job.objects.values())
        return JsonResponse(jobs, safe=False)

    elif request.method == 'POST':
        data = json.loads(request.body)
        job = Job.objects.create(
            title=data.get('title'),
            description=data.get('description'),
            location=data.get('location'),
            hourly_rate=data.get('hourly_rate')
        )
        return JsonResponse({'message': 'Job created successfully', 'job_id': job.id}, status=201)


# GET, PUT, or DELETE a specific job by ID
@csrf_exempt
def job_detail(request, id):
    job = get_object_or_404(Job, pk=id)

    if request.method == 'GET':
        return JsonResponse({
            'id': job.id,
            'title': job.title,
            'description': job.description,
            'location': job.location,
            'hourly_rate': str(job.hourly_rate) if job.hourly_rate else None,
        })

    elif request.method == 'PUT':
        data = json.loads(request.body)
        job.title = data.get('title', job.title)
        job.description = data.get('description', job.description)
        job.location = data.get('location', job.location)
        job.hourly_rate = data.get('hourly_rate', job.hourly_rate)
        job.save()
        return JsonResponse({'message': 'Job updated successfully'})

    elif request.method == 'DELETE':
        job.delete()
        return JsonResponse({'message': 'Job deleted successfully'})
