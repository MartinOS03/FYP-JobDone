from django.db import models
from django.contrib.auth.models import User

# REF-001: Django Models Documentation - Model class definition and field types
class Profile(models.Model):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('tradesman', 'Tradesman'),
    )

    # REF-001: OneToOneField relationship to User model
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    # TRADESMAN PROFILE FIELDS
    # These fields are only used when role='tradesman'
    # They show up on the public profile page and in search results
    company_name = models.CharField(max_length=150, blank=True, null=True)
    trade = models.CharField(max_length=100, blank=True, null=True)
    service_area = models.CharField(max_length=150, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    availability = models.CharField(max_length=120, blank=True, null=True)
    years_experience = models.PositiveIntegerField(blank=True, null=True)
    services_offered = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    # REF-001: Django Models - ImageField for file uploads (Iteration 4 US 30)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    # Helper property - shows company name if they have one, otherwise their name
    # Used throughout the app to display tradesman names consistently
    @property
    def display_name(self):
        if self.company_name:
            return self.company_name
        return self.user.get_full_name() or self.user.username

    # Calculate average rating from all completed job reviews
    # Returns None if no reviews exist yet
    # This is used in search results and on profile pages
    # REF-005: Django ORM queries for filtering
    # REF-022: Django ORM aggregation (Avg) for calculating average rating
    @property
    def average_rating(self):
        from jobs.models import JobReview
        reviews = JobReview.objects.filter(job_request__job__owner=self.user)
        if not reviews.exists():
            return None
        return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)

    # Calculate profile completion percentage for tradesmen
    # Counts how many important fields are filled out
    # Returns a number between 0 and 100
    # REF-029: ChatGPT - Profile completion algorithm logic
    @property
    def completion_percentage(self):
        if self.role != 'tradesman':
            return 100  # Customers don't need profile completion
        
        # Important fields for tradesmen profiles
        fields = [
            self.company_name or self.user.get_full_name(),
            self.trade,
            self.service_area or self.location,
            self.bio,
            self.services_offered,
            self.years_experience,
            self.availability,
            self.contact_email,
        ]
        
        filled_count = sum(1 for field in fields if field)
        total_fields = len(fields)
        
        return int((filled_count / total_fields) * 100) if total_fields > 0 else 0


# Notification model - tracks user notifications for messages and job requests
# Users get notified when they receive new messages or job requests
# REF-001: Django Models Documentation - Model definition
# REF-028: ChatGPT - Notification system design
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('message', 'New Message'),
        ('job_request', 'New Job Request'),
        ('job_status', 'Job Status Update'),
    )

    # REF-001: ForeignKey relationship to User model
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # Optional link to related object (e.g., job request ID, chat username)
    link = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']  # Most recent first

    def __str__(self):
        return f"{self.user.username} - {self.get_notification_type_display()} ({'read' if self.is_read else 'unread'})"


# Iteration 4 (US 29): Customers can save favourite tradesmen for quick rebooking
# REF-001: Django Models Documentation - Model definition and ForeignKey relationships
# REF-031: ChatGPT - Iteration 4 favourites feature design
class Favourite(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourite_tradesmen')
    tradesman = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['customer', 'tradesman']]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.username} favs {self.tradesman.username}"


# Iteration 4 (US 27): Tradesmen upload qualifications; admin verifies
# REF-001: Django Models - Model definition, FileField for document upload
# REF-031: ChatGPT - Iteration 4 qualification verification workflow
class Qualification(models.Model):
    tradesman = models.ForeignKey(User, on_delete=models.CASCADE, related_name='qualifications')
    title = models.CharField(max_length=200, help_text='e.g. City & Guilds Plumbing Level 2')
    document = models.FileField(upload_to='qualifications/%Y/%m/', help_text='Certificate or proof document')
    verified = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} ({self.tradesman.username}) - {'Verified' if self.verified else 'Pending'}"
