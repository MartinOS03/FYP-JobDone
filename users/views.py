from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, Notification, Favourite, Qualification
from django.db import models
from django.db.models import Avg, Q
from jobs.models import Job, JobRequest, JobReview, JobRequestImage
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import uuid


# Helper function to create unique confirmation codes when tradesmen mark jobs as complete
# Customer needs to enter this code to verify the work is done before leaving a review
# REF-019: Python UUID module for generating unique codes
# REF-027: ChatGPT - Confirmation code generation logic
def generate_confirmation_code():
    while True:
        code = uuid.uuid4().hex[:8].upper()
        # Keep generating until we get a unique one
        if not JobRequest.objects.filter(confirmation_code=code).exists():
            return code
import json


# Helper function to send email notifications
# Sends an email when a notification is created for important events
# REF-008: Django Email Backend - send_mail function
def send_notification_email(user, subject, message_text):
    try:
        if user.email:
            send_mail(
                subject=subject,
                message=message_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,  # Don't crash if email fails
            )
    except Exception:
        # Silently fail - email is optional, notifications still work
        pass


# User registration - handles both JSON API calls and form submissions
# Creates a new user and their profile with role (customer or tradesman)
# REF-002: Django Authentication - User creation
# REF-003: Django Views - Request handling
# REF-006: Django Decorators - @csrf_exempt
# REF-020: Python JSON module - JSON parsing
@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            # Try to parse as JSON first (for API calls), fall back to form data
            try:
                data = json.loads(request.body)
                username = data.get('username')
                password = data.get('password')
                role = data.get('role', 'customer')
            except json.JSONDecodeError:
                # If not JSON, get from form POST data
                username = request.POST.get('username')
                password = request.POST.get('password')
                role = request.POST.get('role', 'customer')

            if not username or not password:
                return JsonResponse({'error': 'Username and password required'}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)

            # REF-002: Django User.objects.create_user() method
            user = User.objects.create_user(username=username, password=password)

            from .models import Profile
            Profile.objects.create(user=user, role=role)

            if request.content_type.startswith('application/x-www-form-urlencoded'):
                return render(request, 'users/success.html', {'message': 'User registered successfully!'})
            else:
                return JsonResponse({'message': 'User created successfully', 'role': role}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)




# User login - authenticates and logs in the user
# Supports both JSON API and form-based login
# REF-002: Django Authentication - authenticate() and login()
# REF-003: Django Views - Request handling
# REF-006: Django Decorators - @csrf_exempt
# REF-016: Dennis Ivy - Django Authentication tutorial
@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        try:
            # Try JSON first, then fall back to form data
            try:
                data = json.loads(request.body)
                username = data.get('username')
                password = data.get('password')
            except json.JSONDecodeError:
                username = request.POST.get('username')
                password = request.POST.get('password')

            # REF-002: Django authenticate() and login() functions
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if request.content_type.startswith('application/x-www-form-urlencoded'):
                    return redirect('/api/users/dashboard/')
                else:
                    return JsonResponse({'message': 'Login successful'})
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)



def register_page(request):
    return render(request, 'users/register.html')

def login_page(request):
    return render(request, 'users/login.html')


# User logout - logs out the current user and redirects to home page
# REF-002: Django Authentication - logout() function
# REF-006: Django Decorators - @login_required
# REF-007: Django Messages Framework - messages.success()
@login_required
def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('/')



# Main dashboard - shows different content based on user role
# This is the central hub where users land after logging in
# REF-003: Django Views - Function-based views
# REF-005: Django ORM - Database queries and filtering
# REF-006: Django Decorators - @login_required
# REF-010: Django Q Objects - Complex queries
# REF-017: Aaron Jack - Separate dashboards for different user types
# REF-021: Django ORM - select_related for query optimization
# REF-022: Django ORM - Aggregation (Avg) for ratings
# REF-025: Stack Overflow - Q objects for multiple field search
# Build search terms from query so "plumbing" also matches "Plumber" (Iteration 4 US 31)
# REF-010: Django Q Objects - term expansion for complex lookups
# REF-030: ChatGPT - Trade filtering / search variant logic
def _search_terms_for_query(query):
    if not query or not query.strip():
        return []
    terms = set()
    for word in query.strip().lower().split():
        if len(word) < 2:
            continue
        terms.add(word)
        # Word variants: "plumbing" -> also match "plumber"; "electrician" -> "electric"
        if word.endswith('ing') and len(word) > 3:
            terms.add(word[:-3])  # plumbing -> plumb
        if word.endswith('er') and len(word) > 2:
            terms.add(word[:-2])  # plumber -> plumb
        if word.endswith('ians'):
            terms.add(word[:-4])  # electricians -> electric
        if word.endswith('ian') and len(word) > 3:
            terms.add(word[:-3])  # electrician -> electric
    return list(terms)


# REF-030: ChatGPT - Trade filtering implementation
@login_required
def dashboard(request):
    profile, created = Profile.objects.get_or_create(user=request.user, defaults={'role': 'customer'})

    # TRADESMAN DASHBOARD SECTION
    # Shows their posted services, open customer jobs and request count
    if profile.role == 'tradesman':
        # Jobs/services this tradesman has posted (their offerings)
        my_jobs = Job.objects.filter(owner=request.user).order_by('-date_posted')

        # Open-ended jobs that customers have posted (potential work opportunities)
        # Filter to only show jobs matching this tradesman's trade
        open_jobs = Job.objects.filter(owner__profile__role='customer').order_by('-date_posted')
        
        # If tradesman has a trade specified, only show jobs matching that trade (Iteration 4: term expansion)
        if profile.trade:
            terms = _search_terms_for_query(profile.trade)
            if terms:
                q_trade = Q()
                for term in terms:
                    q_trade |= Q(trade__icontains=term)
                open_jobs = open_jobs.filter(q_trade)

        # Count of how many job requests customers have sent them
        request_count = JobRequest.objects.filter(job__owner=request.user).count()
        
        # Get unread notification count
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()

        return render(request, 'users/tradesman_dashboard.html', {
            'my_jobs': my_jobs,
            'open_jobs': open_jobs,
            'request_count': request_count,
            'unread_notifications': unread_notifications
        })

    # CUSTOMER DASHBOARD SECTION
    # Shows searchable tradesman directory with filters, plus their job request history
    else:
        # Get search filters from URL parameters
        query = request.GET.get('q', '').strip()
        trade_filter = request.GET.get('trade', '').strip()
        location_filter = request.GET.get('location', '').strip()
        min_rating = request.GET.get('min_rating', '').strip()
        min_experience = request.GET.get('min_experience', '').strip()
        availability_filter = request.GET.get('availability', '').strip()

        # Start with all tradesmen, calculate their average rating in one query
        # select_related optimises the database query to avoid multiple hits
        # REF-005: Django ORM - filter() and order_by()
        # REF-021: Django ORM - select_related() for query optimization
        # REF-022: Django ORM - annotate() with Avg() for calculating average rating
        tradesmen = (
            Profile.objects.filter(role='tradesman')
            .select_related('user')
            .annotate(avg_rating=Avg('user__jobs__requests__review__rating'))
            .order_by('-avg_rating', 'user__username')  # Best rated first
        )

        # Multi-field search - case-insensitive; expanded terms so "plumbing" matches "Plumber" (Iteration 4)
        # REF-005: Django ORM - filter() with multiple conditions
        # REF-010: Django Q Objects - Complex OR queries across multiple fields
        if query:
            terms = _search_terms_for_query(query)
            if terms:
                q_obj = Q()
                for term in terms:
                    q_obj |= (
                        Q(company_name__icontains=term) |
                        Q(user__first_name__icontains=term) |
                        Q(user__last_name__icontains=term) |
                        Q(user__username__icontains=term) |
                        Q(trade__icontains=term) |
                        Q(service_area__icontains=term)
                    )
                tradesmen = tradesmen.filter(q_obj)

        # Filter by specific trade type - case-insensitive with term expansion (Iteration 4)
        if trade_filter:
            terms = _search_terms_for_query(trade_filter)
            if terms:
                q_trade = Q()
                for term in terms:
                    q_trade |= Q(trade__icontains=term)
                tradesmen = tradesmen.filter(q_trade)

        # Filter by location (checks both location and service_area fields)
        # REF-010: Django Q Objects - OR condition for multiple fields
        if location_filter:
            tradesmen = tradesmen.filter(
                Q(location__icontains=location_filter) |
                Q(service_area__icontains=location_filter)
            )

        # Filter by minimum rating - only show tradesmen with rating >= min_rating
        if min_rating:
            try:
                min_rating_value = float(min_rating)
                tradesmen = tradesmen.filter(avg_rating__gte=min_rating_value)
            except ValueError:
                messages.warning(request, 'Invalid rating filter ignored.')

        # Filter by minimum years of experience
        if min_experience:
            try:
                min_exp_value = int(min_experience)
                tradesmen = tradesmen.filter(years_experience__gte=min_exp_value)
            except ValueError:
                messages.warning(request, 'Invalid experience filter ignored.')

        # Filter by availability status
        if availability_filter:
            tradesmen = tradesmen.filter(availability__icontains=availability_filter)

        # Get all job requests this customer has made (for tracking status)
        my_requests = (
            JobRequest.objects.select_related('job', 'job__owner')
            .filter(customer=request.user)
            .order_by('-date_requested')
        )
        # REF-005: Django ORM - values_list() for favourite IDs (Iteration 4 US 29)
        favourite_tradesman_ids = set(
            Favourite.objects.filter(customer=request.user).values_list('tradesman_id', flat=True)
        )
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()

        return render(request, 'users/customer_dashboard.html', {
            'tradesmen': tradesmen,
            'filters': {
                'q': query,
                'trade': trade_filter,
                'location': location_filter,
                'min_rating': min_rating,
                'min_experience': min_experience,
                'availability': availability_filter,
            },
            'rating_choices': range(1, 6),
            'my_requests': my_requests,
            'unread_notifications': unread_notifications,
            'favourite_tradesman_ids': favourite_tradesman_ids,
        })



# Tradesmen can post their services/jobs here
# This creates a job listing that customers can search for and request
# REF-003: Django Views - Function-based views
# REF-005: Django ORM - create() method
# REF-006: Django Decorators - @login_required
# REF-007: Django Messages Framework
@login_required
def create_job(request):
    profile, created = Profile.objects.get_or_create(user=request.user, defaults={'role': 'customer'})

    # Security check - only tradesmen can post services
    if profile.role != 'tradesman':
        return JsonResponse({'error': 'Only tradesmen can create jobs'}, status=403)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')
        hourly_rate = request.POST.get('hourly_rate')

        if not title or not description or not location:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'users/create_job.html')

        Job.objects.create(
            title=title,
            description=description,
            location=location,
            hourly_rate=hourly_rate if hourly_rate else None,
            owner=request.user,
        )
        messages.success(request, 'Job created successfully!')
        return redirect('/api/users/dashboard/')

    return render(request, 'users/create_job.html')



# Tradesmen can see all job requests customers have sent them
# Shows who wants their services and what they're asking for
@login_required
def view_requests(request):
    profile, created = Profile.objects.get_or_create(user=request.user, defaults={'role': 'customer'})

    if profile.role != 'tradesman':
        return JsonResponse({'error': 'Only tradesmen can view job requests'}, status=403)

    # Get all requests for jobs owned by this tradesman, ordered by most recent
    requests = JobRequest.objects.select_related('job', 'customer').filter(job__owner=request.user).order_by('-date_requested')

    return render(request, 'users/view_requests.html', {'requests': requests})


# Detailed view of a specific job request
# Tradesmen can see full details and mark it as complete from here
@login_required
def request_detail(request, request_id):
    profile, created = Profile.objects.get_or_create(user=request.user, defaults={'role': 'customer'})

    if profile.role != 'tradesman':
        return JsonResponse({'error': 'Only tradesmen can view job requests'}, status=403)

    # Make sure this request belongs to a job owned by this tradesman
    try:
        job_request = JobRequest.objects.select_related('job', 'customer').get(id=request_id, job__owner=request.user)
    except JobRequest.DoesNotExist:
        return JsonResponse({'error': 'Request not found or access denied'}, status=404)

    return render(request, 'users/request_detail.html', {'job_request': job_request})


# When a tradesman finishes a job, they mark it complete here
# This generates a confirmation code that the customer must enter to verify completion
# Status changes to 'awaiting_confirmation' until customer enters the code
# REF-003: Django Views - Function-based views
# REF-005: Django ORM - get() and save() methods
# REF-006: Django Decorators - @login_required
# REF-007: Django Messages Framework
# REF-019: Python UUID - Confirmation code generation
# REF-028: ChatGPT - Notification creation
@login_required
def complete_request(request, request_id):
    profile, created = Profile.objects.get_or_create(user=request.user, defaults={'role': 'customer'})

    if profile.role != 'tradesman':
        return JsonResponse({'error': 'Only tradesmen can update job requests'}, status=403)

    try:
        job_request = JobRequest.objects.select_related('job').get(id=request_id, job__owner=request.user)
    except JobRequest.DoesNotExist:
        return JsonResponse({'error': 'Request not found or access denied'}, status=404)

    # Don't allow completing an already completed job
    if job_request.status == 'completed':
        messages.info(request, 'This request has already been confirmed by the customer.')
        return redirect('request_detail', request_id=request_id)

    # Update status and timestamp
    job_request.status = 'awaiting_confirmation'
    job_request.completed_at = timezone.now()

    # Generate confirmation code if one doesn't exist (only generate once)
    if not job_request.confirmation_code:
        job_request.confirmation_code = generate_confirmation_code()
        job_request.confirmation_generated_at = timezone.now()

    job_request.save()
    
    # Notify customer that job is awaiting confirmation
    # REF-028: ChatGPT - Notification creation for job status updates
    Notification.objects.create(
        user=job_request.customer,
        notification_type='job_status',
        message=f'Your job "{job_request.job.title}" is awaiting confirmation. Enter the code to verify completion.',
        link=f'/api/users/request/{job_request.id}/confirm/'
    )
    # Send email notification
    # REF-008: Django Email Backend
    send_notification_email(
        job_request.customer,
        f'Job Awaiting Confirmation: {job_request.job.title}',
        f'Your job "{job_request.job.title}" has been marked as complete by {request.user.get_full_name() or request.user.username}.\n\nPlease enter the confirmation code to verify completion and leave a review.\n\nConfirmation code: {job_request.confirmation_code}'
    )

    return render(request, 'users/awaiting_confirmation.html', {
        'job_request': job_request,
        'confirmation_code': job_request.confirmation_code
    })


# Customer enters the confirmation code here to verify the job is done
# Once verified, status changes to 'completed' and they can leave a review
@login_required
def confirm_completion(request, request_id):
    profile, created = Profile.objects.get_or_create(user=request.user, defaults={'role': 'customer'})

    if profile.role != 'customer':
        return JsonResponse({'error': 'Only customers can confirm job completion'}, status=403)

    try:
        job_request = JobRequest.objects.select_related('job', 'job__owner').get(id=request_id, customer=request.user)
    except JobRequest.DoesNotExist:
        return JsonResponse({'error': 'Request not found or access denied'}, status=404)

    # Only allow confirmation if status is 'awaiting_confirmation'
    if job_request.status != 'awaiting_confirmation':
        messages.info(request, 'This job is not awaiting confirmation.')
        return redirect('dashboard')

    if request.method == 'POST':
        submitted_code = request.POST.get('confirmation_code', '').strip().upper()

        # Validate the confirmation code
        if not submitted_code:
            messages.error(request, 'Confirmation code is required.')
        elif submitted_code != (job_request.confirmation_code or ''):
            messages.error(request, 'Invalid confirmation code, please try again.')
        else:
            # Code matches - mark as completed and redirect to review page
            job_request.status = 'completed'
            job_request.confirmed_at = timezone.now()
            job_request.save()
            
            # Notify tradesman that job was confirmed
            # REF-028: ChatGPT - Notification creation
            Notification.objects.create(
                user=job_request.job.owner,
                notification_type='job_status',
                message=f'Your job "{job_request.job.title}" has been confirmed as completed by {request.user.get_full_name() or request.user.username}.',
                link=f'/api/users/request/{job_request.id}/'
            )
            # Send email notification
            # REF-008: Django Email Backend
            send_notification_email(
                job_request.job.owner,
                f'Job Confirmed: {job_request.job.title}',
                f'Your job "{job_request.job.title}" has been confirmed as completed by {request.user.get_full_name() or request.user.username}.\n\nThe customer will now be able to leave a review.'
            )
            
            messages.success(request, 'Job confirmed! Please leave a review for your tradesman.')
            return redirect('submit_review', request_id=job_request.id)

    return render(request, 'users/confirm_completion.html', {
        'job_request': job_request
    })


# Customer leaves a rating and review after job is confirmed complete
# OneToOne relationship prevents duplicate reviews (one review per job)
# REF-003: Django Views - Function-based views
# REF-005: Django ORM - create() method
# REF-006: Django Decorators - @login_required
# REF-007: Django Messages Framework
# REF-026: Stack Overflow - OneToOneField prevents duplicate reviews
@login_required
def submit_review(request, request_id):
    profile, created = Profile.objects.get_or_create(user=request.user, defaults={'role': 'customer'})

    if profile.role != 'customer':
        return JsonResponse({'error': 'Only customers can submit reviews'}, status=403)

    try:
        job_request = JobRequest.objects.select_related('job', 'job__owner').get(id=request_id, customer=request.user)
    except JobRequest.DoesNotExist:
        return JsonResponse({'error': 'Request not found or access denied'}, status=404)

    # Can only review completed jobs
    if job_request.status != 'completed':
        messages.info(request, 'You can only review completed jobs.')
        return redirect('dashboard')

    # Check if review already exists (OneToOne prevents duplicates)
    if hasattr(job_request, 'review'):
        messages.info(request, 'You have already submitted a review for this job.')
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            rating = int(request.POST.get('rating'))
        except (TypeError, ValueError):
            rating = None

        comment = request.POST.get('comment', '').strip()
        # REF-003: Django Views - request.FILES for file upload (Iteration 4 US 28)
        photo = request.FILES.get('photo')

        if rating is None or rating < 1 or rating > 5:
            messages.error(request, 'Please provide a rating between 1 and 5.')
        else:
            JobReview.objects.create(
                job_request=job_request,
                rating=rating,
                comment=comment,
                photo=photo,
            )
            messages.success(request, 'Thank you for leaving a review!')
            return redirect('dashboard')

    return render(request, 'users/submit_review.html', {
        'job_request': job_request,
        'rating_options': range(1, 6)
    })


# Customer sends a job request to a tradesman
# This creates a JobRequest that the tradesman can see and respond to
# REF-003: Django Views - Function-based views
# REF-005: Django ORM - create() method
# REF-006: Django Decorators - @login_required
# REF-007: Django Messages Framework
# REF-028: ChatGPT - Notification creation
@login_required
def request_job(request, job_id):
    profile, created = Profile.objects.get_or_create(
        user=request.user, defaults={'role': 'customer'}
    )

    if profile.role != 'customer':
        return JsonResponse({'error': 'Only customers can request jobs'}, status=403)

    job = Job.objects.get(id=job_id)

    if request.method == 'POST':
        message = request.POST.get('message')
        if not message:
            messages.error(request, 'Message cannot be empty.')
            return render(request, 'users/request_job.html', {'job': job})

        job_request = JobRequest.objects.create(job=job, customer=request.user, message=message)
        # Iteration 4 (US 28): Attach optional photos to job request
        # REF-005: Django ORM - create() for related JobRequestImage records
        for f in request.FILES.getlist('images'):
            if f and f.size:
                JobRequestImage.objects.create(job_request=job_request, image=f)
        # Create notification for the tradesman
        # REF-028: ChatGPT - Notification system design and creation
        notification = Notification.objects.create(
            user=job.owner,
            notification_type='job_request',
            message=f'New job request from {request.user.get_full_name() or request.user.username} for "{job.title}"',
            link=f'/api/users/request/{job_request.id}/'
        )
        # Send email notification
        # REF-008: Django Email Backend - send_mail via helper function
        send_notification_email(
            job.owner,
            f'New Job Request: {job.title}',
            f'You have received a new job request from {request.user.get_full_name() or request.user.username} for "{job.title}".\n\nMessage: {message}\n\nView the request in your dashboard.'
        )
        messages.success(request, 'Request sent successfully!')
        return redirect('/api/users/dashboard/')

    return render(request, 'users/request_job.html', {'job': job})



# Tradesmen update profile; Iteration 4: photo upload and qualification management
# REF-003: Django Views - Function-based views, request.FILES handling
# REF-005: Django ORM - get(), save(), create(), filter(), delete()
# REF-006: Django Decorators - @login_required
# REF-007: Django Messages Framework
@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if profile.role != 'tradesman':
        return JsonResponse({'error': 'Only tradesmen can edit their profiles'}, status=403)

    if request.method == 'POST':
        # Delete qualification (separate form submit - don't overwrite profile)
        delete_qual_id = request.POST.get('delete_qualification_id')
        if delete_qual_id:
            try:
                q = Qualification.objects.get(id=int(delete_qual_id), tradesman=request.user)
                q.delete()
                messages.success(request, 'Qualification removed.')
            except (Qualification.DoesNotExist, ValueError):
                pass
            return redirect('edit_profile')

        profile.company_name = request.POST.get('company_name')
        profile.trade = request.POST.get('trade')
        profile.services_offered = request.POST.get('services_offered')
        profile.service_area = request.POST.get('service_area')
        profile.location = request.POST.get('location')
        profile.hourly_rate = request.POST.get('hourly_rate') or None
        profile.availability = request.POST.get('availability')
        years_experience_input = request.POST.get('years_experience')
        try:
            profile.years_experience = int(years_experience_input) if years_experience_input else None
        except (TypeError, ValueError):
            messages.warning(request, 'Years of experience must be a number. Value ignored.')
        profile.bio = request.POST.get('bio')
        profile.contact_email = request.POST.get('contact_email')
        if request.FILES.get('photo'):
            profile.photo = request.FILES['photo']
        profile.save()
        qual_title = request.POST.get('qualification_title', '').strip()
        # REF-005: Django ORM - create() for Qualification (Iteration 4 US 27)
        if qual_title and request.FILES.get('qualification_document'):
            Qualification.objects.create(
                tradesman=request.user,
                title=qual_title,
                document=request.FILES['qualification_document'],
            )
            messages.success(request, 'Qualification uploaded. It will show as pending until verified.')
        messages.success(request, 'Profile updated successfully!')
        return redirect('/api/users/dashboard/')

    # REF-005: Django ORM - filter() and order_by() for qualification list
    qualifications = Qualification.objects.filter(tradesman=request.user).order_by('-uploaded_at')
    return render(request, 'users/edit_profile.html', {'profile': profile, 'qualifications': qualifications})


# Public profile page for a tradesman (Iteration 4: qualifications, photo, favourite state)
# REF-003: Django Views - Function-based views
# REF-005: Django ORM - filter(), get(), exists()
# REF-006: Django Decorators - @login_required
# REF-021: Django ORM - select_related() for query optimization
@login_required
def tradesman_profile_detail(request, profile_id):
    try:
        tradesman_profile = Profile.objects.select_related('user').get(id=profile_id, role='tradesman')
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Tradesman not found'}, status=404)

    reviews = (
        JobReview.objects.filter(job_request__job__owner=tradesman_profile.user)
        .select_related('job_request__customer')
        .order_by('-created_at')
    )
    # REF-005: Django ORM - filter() for verified qualifications (Iteration 4 US 27)
    qualifications = Qualification.objects.filter(tradesman=tradesman_profile.user, verified=True).order_by('-verified_at')
    # REF-005: Django ORM - exists() for favourite check (Iteration 4 US 29)
    is_favourite = False
    if request.user.is_authenticated and getattr(request.user, 'profile', None):
        try:
            p = Profile.objects.get(user=request.user)
            if p.role == 'customer':
                is_favourite = Favourite.objects.filter(customer=request.user, tradesman=tradesman_profile.user).exists()
        except Profile.DoesNotExist:
            pass

    return render(request, 'users/tradesman_profile.html', {
        'tradesman': tradesman_profile,
        'reviews': reviews,
        'qualifications': qualifications,
        'is_favourite': is_favourite,
    })
# Standalone search page for finding tradesmen (Iteration 4: term expansion, favourite IDs)
# REF-003: Django Views - Function-based views
# REF-005: Django ORM - filter(), annotate(), values_list()
# REF-006: Django Decorators - @login_required
# REF-010: Django Q Objects - multi-field search with expanded terms
# REF-021: Django ORM - select_related(); REF-022: annotate with Avg()
@login_required
def search_tradesmen(request):
    # Get search parameters from URL
    query = request.GET.get('q', '').strip()
    trade_filter = request.GET.get('trade', '').strip()
    location_filter = request.GET.get('location', '').strip()
    min_rating = request.GET.get('min_rating', '').strip()

    # Base query - all tradesmen with average rating calculated
    tradesmen = (
        Profile.objects.filter(role='tradesman')
        .select_related('user')
        .annotate(avg_rating=Avg('user__jobs__requests__review__rating'))
        .order_by('-avg_rating', 'user__username')
    )

    # Case-insensitive search with term expansion:
    if query:
        terms = _search_terms_for_query(query)
        if terms:
            q_obj = Q()
            for term in terms:
                q_obj |= (
                    Q(company_name__icontains=term) |
                    Q(user__first_name__icontains=term) |
                    Q(user__last_name__icontains=term) |
                    Q(user__username__icontains=term) |
                    Q(trade__icontains=term) |
                    Q(service_area__icontains=term)
                )
            tradesmen = tradesmen.filter(q_obj)

    if trade_filter:
        terms = _search_terms_for_query(trade_filter)
        if terms:
            q_trade = Q()
            for term in terms:
                q_trade |= Q(trade__icontains=term)
            tradesmen = tradesmen.filter(q_trade)

    if location_filter:
        tradesmen = tradesmen.filter(
            Q(location__icontains=location_filter) |
            Q(service_area__icontains=location_filter)
        )

    if min_rating:
        try:
            min_rating_value = float(min_rating)
            tradesmen = tradesmen.filter(avg_rating__gte=min_rating_value)
        except ValueError:
            messages.warning(request, 'Invalid rating filter ignored.')

    # REF-005: Django ORM - values_list() for favourite IDs (Iteration 4 US 29)
    favourite_tradesman_ids = set()
    if request.user.is_authenticated:
        favourite_tradesman_ids = set(
            Favourite.objects.filter(customer=request.user).values_list('tradesman_id', flat=True)
        )
    return render(request, 'users/search_tradesmen.html', {
        'tradesmen': tradesmen,
        'filters': {
            'q': query,
            'trade': trade_filter,
            'location': location_filter,
            'min_rating': min_rating,
        },
        'rating_choices': range(1, 6),
        'favourite_tradesman_ids': favourite_tradesman_ids,
    })

# Iteration 4 (US 29): Toggle favourite tradesman (add or remove)
# REF-003: Django Views - Function-based views, redirect()
# REF-005: Django ORM - get_or_create(), delete()
# REF-006: Django Decorators - @login_required
# REF-007: Django Messages Framework
@login_required
def toggle_favourite(request, tradesman_id):
    profile, _ = Profile.objects.get_or_create(user=request.user, defaults={'role': 'customer'})
    if profile.role != 'customer':
        messages.error(request, 'Only customers can save favourite tradesmen.')
        next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or '/api/users/dashboard/'
        return redirect(next_url)
    try:
        tradesman = User.objects.get(id=tradesman_id)
        tradesman_profile = Profile.objects.get(user=tradesman, role='tradesman')
    except (User.DoesNotExist, Profile.DoesNotExist):
        messages.error(request, 'Tradesman not found.')
        return redirect('dashboard')
    fav, created = Favourite.objects.get_or_create(customer=request.user, tradesman=tradesman)
    if not created:
        fav.delete()
        messages.success(request, f'Removed {tradesman_profile.display_name} from favourites.')
    else:
        messages.success(request, f'Added {tradesman_profile.display_name} to favourites.')
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or '/api/users/dashboard/'
    return redirect(next_url)


# Iteration 4 (US 29): List of customer's favourite tradesmen for quick rebooking
# REF-003: Django Views - Function-based views
# REF-005: Django ORM - filter(), select_related()
# REF-006: Django Decorators - @login_required
# REF-022: Django ORM - aggregation (Avg) for rating display
@login_required
def favourites_list(request):
    profile, _ = Profile.objects.get_or_create(user=request.user, defaults={'role': 'customer'})
    if profile.role != 'customer':
        return JsonResponse({'error': 'Only customers can view favourites'}, status=403)
    from django.db.models import Avg
    favs = (
        Favourite.objects.filter(customer=request.user)
        .select_related('tradesman')
        .order_by('-created_at')
    )
    # Get profile and avg rating for each tradesman
    tradesmen_data = []
    for fav in favs:
        try:
            p = Profile.objects.get(user=fav.tradesman, role='tradesman')
            avg_rating = JobReview.objects.filter(
                job_request__job__owner=fav.tradesman
            ).aggregate(avg=Avg('rating'))['avg']
            tradesmen_data.append({'profile': p, 'avg_rating': round(avg_rating, 1) if avg_rating else None})
        except Profile.DoesNotExist:
            continue
    return render(request, 'users/favourites_list.html', {'tradesmen_data': tradesmen_data})


# Customers can post open-ended jobs here
# These show up on the "Open Jobs Board" where tradesmen can browse and contact them
@login_required
def post_open_job(request):
    profile, created = Profile.objects.get_or_create(user=request.user, defaults={'role': 'customer'})

    if profile.role != 'customer':
        return JsonResponse({'error': 'Only customers can post open jobs'}, status=403)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')
        hourly_rate = request.POST.get('hourly_rate')
        trade = request.POST.get('trade', '').strip()

        if not title or not description or not location:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'users/post_open_job.html')

        Job.objects.create(
            title=title,
            description=description,
            location=location,
            hourly_rate=hourly_rate if hourly_rate else None,
            owner=request.user,
            trade=trade if trade else None,
        )

        messages.success(request, 'Your job has been posted to the Open Jobs Board!')
        return redirect('/api/users/dashboard/')

    return render(request, 'users/post_open_job.html')


# Tradesmen can browse all open-ended jobs that customers have posted
# This is where they can find new work opportunities
@login_required
def open_jobs_board(request):
    profile, created = Profile.objects.get_or_create(user=request.user, defaults={'role': 'customer'})

    if profile.role != 'tradesman':
        return JsonResponse({'error': 'Only tradesmen can view the open jobs board'}, status=403)

    # Get all jobs posted by customers (not tradesmen)
    open_jobs = Job.objects.filter(owner__profile__role='customer').order_by('-date_posted')
    # If tradesman has a trade specified, only show jobs matching that trade (Iteration 4: term expansion)
    if profile.trade:
        terms = _search_terms_for_query(profile.trade)
        if terms:
            q_trade = Q()
            for term in terms:
                q_trade |= Q(trade__icontains=term)
            open_jobs = open_jobs.filter(q_trade)

    return render(request, 'users/open_jobs_board.html', {'open_jobs': open_jobs})


# Display all notifications for the current user
# Shows both read and unread notifications, with unread ones highlighted
# REF-003: Django Views - Function-based views
# REF-005: Django ORM - filter() and order_by()
# REF-006: Django Decorators - @login_required
# REF-028: ChatGPT - Notification system design
@login_required
def notifications(request):
    notifications_list = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'users/notifications.html', {'notifications': notifications_list})


# Mark a notification as read when user clicks on it
# Also redirects to the link if one is provided
# REF-003: Django Views - Function-based views
# REF-005: Django ORM - get() and save() methods
# REF-006: Django Decorators - @login_required
# REF-007: Django Messages Framework
@login_required
def mark_notification_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        
        # Redirect to the link if provided, otherwise back to notifications
        if notification.link:
            return redirect(notification.link)
        return redirect('notifications')
    except Notification.DoesNotExist:
        messages.error(request, 'Notification not found.')
        return redirect('dashboard')
