from django.db import models
from django.contrib.auth.models import User


# Job model - represents a service offering or job posting
# Can be posted by tradesmen (their services) or customers open-ended jobs
# REF-001: Django Models Documentation - Model class definition
class Job(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    # Owner can be a tradesman (their service) or customer when open job posting
    # REF-001: ForeignKey relationship with CASCADE delete
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs', null=True, blank=True)
    # Trade field - specifies what type of trade this job is for (plumber, electrician, etc.)
    # Used to filter open jobs so tradesmen only see jobs relevant to their trade
    trade = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.location}"



# JobRequest model - tracks when a customer requests a tradesman's service
# Status workflow: pending → in_progress → awaiting_confirmation → completed
# The confirmation code system ensures jobs are verified before reviews
# REF-001: Django Models Documentation - Model with choices field
class JobRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('awaiting_confirmation', 'Awaiting Confirmation'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='requests')
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    date_requested = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending')
    # Confirmation code generated when tradesman marks job complete
    # Customer must enter this to verify completion before leaving review
    confirmation_code = models.CharField(max_length=12, unique=True, blank=True, null=True)
    confirmation_generated_at = models.DateTimeField(blank=True, null=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Request from {self.customer.username} for {self.job.title} ({self.status})"


# JobReview model - stores customer reviews after job completion
# REF-001: Django Models - OneToOneField prevents duplicate reviews; ImageField (Iteration 4 US 28)
class JobReview(models.Model):
    job_request = models.OneToOneField(JobRequest, on_delete=models.CASCADE, related_name='review')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    photo = models.ImageField(upload_to='reviews/%Y/%m/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # Most recent reviews first

    def __str__(self):
        return f"Review for {self.job_request.job.title} ({self.rating}/5)"


# Iteration 4 (US 28): Photos attached to job requests (customers upload when requesting)
# REF-001: Django Models Documentation - ForeignKey and ImageField
class JobRequestImage(models.Model):
    job_request = models.ForeignKey(JobRequest, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='job_requests/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for request #{self.job_request_id}"


# Open-ended job completion - tracks when tradesmen complete customer-posted open jobs
# Similar workflow to JobRequest: tradesman marks done → generates code → customer verifies → review
# REF-001: Django Models Documentation - Model with choices field
class OpenJobCompletion(models.Model):
    STATUS_CHOICES = [
        ('awaiting_confirmation', 'Awaiting Confirmation'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='completions')
    tradesman = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completed_open_jobs')
    confirmation_code = models.CharField(max_length=12, unique=True, blank=True, null=True)
    confirmation_generated_at = models.DateTimeField(blank=True, null=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='awaiting_confirmation')

    class Meta:
        unique_together = [['job', 'tradesman']]  # One completion per tradesman per job
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.tradesman.username} completed {self.job.title} ({self.status})"

