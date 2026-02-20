# Code References - JobDone Project

This document maps reference numbers used throughout the codebase to their corresponding sources. Each reference number corresponds to a specific website, tutorial, or documentation that was used to help implement that particular code section.

- REF-001 - Django Models Documentation  
URL: https://docs.djangoproject.com/en/5.2/topics/db/models/ 
Used For: Model definitions, field types, relationships (ForeignKey, OneToOneField), model methods, Meta options  
Code Examples: All model classes in `users/models.py`, `jobs/models.py`, `chat/models.py`

- REF-002 - Django Authentication System  
URL: https://docs.djangoproject.com/en/5.2/topics/auth/  
Used For: User authentication, login, logout, user creation, password handling  
Code Examples: `authenticate()`, `login()`, `logout()`, `User.objects.create_user()` in `users/views.py`

- REF-003 - Django Views and URL Routing  
URL: https://docs.djangoproject.com/en/5.2/topics/http/views/  
Used For: Function-based views, URL patterns, request handling, response types  
Code Examples: All view functions in `users/views.py`, `chat/views.py`, URL patterns in `urls.py` files

- REF-004** - Django Template Language  
URL: https://docs.djangoproject.com/en/5.2/topics/templates/  
Used For: Template rendering, template tags, filters, context variables  
Code Examples: All `.html` template files, `render()` function calls

- REF-005 - Django ORM Queries  
URL: https://docs.djangoproject.com/en/5.2/topics/db/queries/  
Used For: Database queries, filtering, Q objects, select_related, annotate, aggregations  
Code Examples: `Job.objects.filter()`, `Profile.objects.select_related()`, `Q()` objects for complex queries

- REF-006 - Django Decorators  
URL: https://docs.djangoproject.com/en/5.2/topics/http/decorators/  
Used For: `@login_required`, `@csrf_exempt`, view decorators  
Code Examples: All `@login_required` decorators, `@csrf_exempt` in views

- REF-007 - Django Messages Framework  
URL: https://docs.djangoproject.com/en/5.2/ref/contrib/messages/  
Used For: Flash messages, success/error notifications to users  
Code Examples: `messages.success()`, `messages.error()`, `messages.warning()` throughout views

- REF-008 - Django Email Backend  
URL: https://docs.djangoproject.com/en/5.2/topics/email/  
Used For: Email configuration, send_mail function, email backend setup  
Code Examples: `send_mail()` function, email settings in `core/settings.py`

- REF-009 - Django Database Migrations  
URL: https://docs.djangoproject.com/en/5.2/topics/migrations/  
Used For: Creating and applying database migrations, schema changes  
Code Examples: Migration files in `migrations/` directories

- REF-010 - Django Q Objects for Complex Queries  
URL: https://docs.djangoproject.com/en/5.2/topics/db/queries/#complex-lookups-with-q-objects  
Used For: Complex OR/AND queries, filtering across multiple fields  
Code Examples: Multi-field search queries in `dashboard()` view, chat message filtering

### Web Development & HTML/CSS

- REF-011 - MDN Web Docs - HTML5  
URL: https://developer.mozilla.org/en-US/docs/Web/HTML  
Used For: HTML5 elements, form elements, semantic HTML  
Code Examples: All HTML template files

- REF-012 - MDN Web Docs - CSS  
URL: https://developer.mozilla.org/en-US/docs/Web/CSS  
Used For: CSS styling, layout techniques, responsive design  
Code Examples: CSS in templates, inline styles

- REF-013 - W3Schools - Django Models  
URL: https://www.w3schools.com/django/django_models.php  
Used For: Model field types, relationships, model methods  
Code Examples: Model definitions

- REF-014 - W3Schools - HTML Forms  
URL: https://www.w3schools.com/html/html_forms.asp  
Used For: Form structure, input types, form submission  
Code Examples: All form elements in templates

### YouTube Tutorials & Video Resources

- REF-015 - Traversy Media - Django Crash Course  
URL: https://www.youtube.com/watch?v=e1IyzVyrLSU  
Used For: Django project structure, models, views, URL patterns, basic Django concepts  
Code Examples: Overall project structure, view patterns, URL routing

- REF-016 - Dennis Ivy - Django Authentication  
URL: https://www.youtube.com/watch?v=tUqUdu0Sjyc  
Used For: User authentication, login/logout, restricting access to pages, role-based access  
Code Examples: `login_user()`, `logout_user()`, `@login_required` decorators, role checks

- REF-017 - Aaron Jack - Separate Dashboards  
URL: https://www.youtube.com/watch?v=Z4pCqK-V_Wo  
Used For: Role-based dashboards, different views for different user types  
Code Examples: `dashboard()` view with role-based logic, separate dashboard templates

- REF-018 - Tom Dekan - Django Chat App  
URL: https://tomdekan.com/articles/instant-messenger  
Used For: Messaging architecture, chat functionality between users  
Code Examples: `ChatMessage` model, `chat_list()`, `chat_detail()` views

### Python & Programming

- REF-019 - Python Documentation - UUID Module  
URL: https://docs.python.org/3/library/uuid.html  
Used For: Generating unique confirmation codes  
Code Examples: `generate_confirmation_code()` function using `uuid.uuid4()`

- REF-020 - Python Documentation - JSON Module  
URL: https://docs.python.org/3/library/json.html  
Used For: JSON parsing, handling JSON requests  
Code Examples: `json.loads()` in `register_user()`, `login_user()` views

### Database & ORM

REF-021 - Django ORM - select_related and prefetch_related  
URL: https://docs.djangoproject.com/en/5.2/ref/models/querysets/#select-related
Used For: Query optimization, reducing database hits  
Code Examples: `.select_related('user')`, `.select_related('job', 'customer')` in queries

- REF-022 - Django ORM - Aggregation (Avg, Count)  
URL: https://docs.djangoproject.com/en/5.2/topics/db/aggregation/ 
Used For: Calculating average ratings, counting objects  
Code Examples: `.annotate(avg_rating=Avg(...))`, `.count()` methods

- REF-023 - Supabase - PostgreSQL Connection  
URL: https://supabase.com/docs/guides/database/connecting-to-postgres
Used For: Database connection string, PostgreSQL setup, dj_database_url  
Code Examples: Database configuration in `core/settings.py`

- REF-024 - dj-database-url Package  
URL: https://github.com/jacobian/dj-database-url  
Used For: Parsing database URLs from environment variables  
Code Examples: `dj_database_url.config()` in `core/settings.py`

### Stack Overflow & Community Resources

- REF-025 - Stack Overflow - Q Objects Multiple Fields  
URL: https://stackoverflow.com/questions/... (Django Q objects filtering)  
Used For: Complex multi-field search queries using Q objects  
Code Examples: Multi-field search in `dashboard()` view with `Q(company_name__icontains=query) | Q(...)`

- REF-026 - Stack Overflow - Django OneToOneField  
URL: https://stackoverflow.com/questions/... (OneToOneField relationships)  
Used For: OneToOne relationships, preventing duplicate reviews  
Code Examples: `JobReview.job_request = OneToOneField()` to prevent duplicate reviews

### AI Assistance

- REF-027 - ChatGPT - Code Structure & Debugging  
URL: https://chatgpt.com/share/6920f27f-3944-800c-80a2-d94b4626261f 
Used For: Code structure suggestions, debugging help, confirmation code generation logic, CSS layout help 
Code Examples: Various code improvements, debugging assistance

- REF-028 - ChatGPT - Notification System Design  
URL: https://chatgpt.com/share/6920f27f-3944-800c-80a2-d94b4626261f 
Used For: Notification model design, notification creation patterns  
Code Examples: `Notification` model structure, notification creation in views

- REF-029 - ChatGPT - Profile Completion Algorithm  
URL: https://chatgpt.com/share/6920f27f-3944-800c-80a2-d94b4626261f
Used For: Profile completion percentage calculation logic  
Code Examples: `completion_percentage` property in `Profile` model

- REF-030 - ChatGPT - Search-term expansion and trade filtering  
URL: https://chatgpt.com/share/6920f27f-3944-800c-80a2-d94b4626261f   
Used For: Design of a search-term expansion helper that generates simple stems from the query and combines expanded terms into Django Q objects for multi-field searching, so related words like “plumber”, “plumbing”, or “plumb” return similar results.  
Code Examples: `_search_terms_for_query()` in `users/views.py`; `trade__icontains` and Q-object search in `dashboard()` and `search_tradesmen()`; open jobs board trade matching.

- REF-031 - ChatGPT - Iteration 4 design and implementation (qualifications, admin actions, file uploads, media)  
URL: https://chatgpt.com/share/6920f27f-3944-800c-80a2-d94b4626261f
Used For: (1) Favourites feature design (Favourite model, toggle/list views). (2) Qualification upload feature: clean Django model with verified flag and use of Django admin actions so admins can mark selected qualifications as verified without a custom admin interface. (3) Multiple image uploads in a single form for job requests: handling multiple files in the view.  
Code Examples: `Favourite`, `Qualification` models; `toggle_favourite`, `favourites_list`; `QualificationAdmin.mark_verified` in `users/admin.py`; `request.FILES.getlist('images')` and `JobRequestImage` in `request_job` view; MEDIA_URL/MEDIA_ROOT in `core/settings.py`; `static()` media serving in `core/urls.py`.


## Reference Usage Summary

### Models (`users/models.py`, `jobs/models.py`, `chat/models.py`)
- REF-001 : All model definitions, ImageField, FileField, ForeignKey, MEDIA settings
- REF-005 : Query methods, relationships
- REF-013 : Model field types
- REF-026 : OneToOneField for reviews
- REF-031 : Favourite, Qualification models (Iteration 4)

### Views (`users/views.py`, `chat/views.py`)
- REF-002 : Authentication functions
- REF-003 : View functions, request handling, redirect(), request.FILES
- REF-005 : Database queries, Q objects, create(), filter(), values_list(), get_or_create()
- REF-006 : Decorators (@login_required, @csrf_exempt)
- REF-007 : Messages framework
- REF-008 : Email sending
- REF-010 : Complex queries with Q objects, search term expansion
- REF-015 : Overall view patterns
- REF-016 : Authentication and access control
- REF-017 : Role-based dashboards
- REF-018 : Chat functionality
- REF-019 : UUID generation
- REF-020 : JSON parsing
- REF-021 : Query optimization (select_related)
- REF-022 : Aggregations (Avg for ratings, favourites list)
- REF-025 : Multi-field search
- REF-027 : Code structure improvements
- REF-028 : Notification creation
- REF-030 : Trade filtering, search variants
- REF-031 : Favourites, qualifications, admin verify action

### Settings (`core/settings.py`)
- REF-001 : MEDIA_URL, MEDIA_ROOT (file uploads)
- REF-008 : Email configuration
- REF-023 : Database connection
- REF-024 : dj_database_url

### Templates (All `.html` files)
- REF-004 : Template language
- REF-011 : HTML5 elements
- REF-012 : CSS styling
- REF-014 : Form elements

### URLs (`urls.py` files)
- REF-003 : URL routing patterns

