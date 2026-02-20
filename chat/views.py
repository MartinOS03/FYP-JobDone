# Chat functionality - allows customers and tradesmen to message each other
# Simple messaging system for discussing job details
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages as django_messages
from .models import ChatMessage, Chat
from users.models import Notification
from django.core.mail import send_mail
from django.conf import settings


# Shows list of all active chats the user has
# Only shows active chats (not marked as JobDone)
# REF-003: Django Views - Function-based views
# REF-005: Django ORM - filter() and order_by()
# REF-006: Django Decorators - @login_required
# REF-010: Django Q Objects - OR condition (user1 OR user2)
# REF-021: Django ORM - select_related() for query optimization
@login_required
def chat_list(request):
    # Get all active chats where user is involved
    chats = Chat.objects.filter(
        Q(user1=request.user) | Q(user2=request.user),
        status='active'
    ).select_related('user1', 'user2').order_by('-created_at')

    # Get the other user and last message for each chat
    chat_data = []
    for chat in chats:
        other_user = chat.get_other_user(request.user)
        last_message = ChatMessage.objects.filter(chat=chat).order_by('-timestamp').first()
        chat_data.append({
            'chat': chat,
            'other_user': other_user,
            'last_message': last_message,
        })

    return render(request, 'chat/chat_list.html', {'chat_data': chat_data})


# Individual chat conversation view
# Shows all messages in the active chat between current user and the specified user
# Creates a new chat if the previous one was marked as JobDone
# REF-003: Django Views - Function-based views
# REF-005: Django ORM - filter(), get_or_create(), order_by()
# REF-006: Django Decorators - @login_required
# REF-010: Django Q Objects - OR condition for bidirectional messages
# REF-018: Tom Dekan - Django chat app tutorial
@login_required
def chat_detail(request, username):
    try:
        receiver = User.objects.get(username=username)
    except User.DoesNotExist:
        from django.http import Http404
        raise Http404("User not found")
    
    # Prevent users from messaging themselves
    if receiver == request.user:
        django_messages.error(request, "You cannot message yourself.")
        return redirect('chat_list')
    
    # Find or create an active chat between these two users
    # Check both user1/user2 combinations since order doesn't matter
    chat = Chat.objects.filter(
        Q(user1=request.user, user2=receiver) | Q(user1=receiver, user2=request.user),
        status='active'
    ).first()
    
    # If no active chat exists, create a new one
    if not chat:
        chat, created = Chat.objects.get_or_create(
            user1=request.user if request.user.id < receiver.id else receiver,
            user2=receiver if request.user.id < receiver.id else request.user,
            defaults={'status': 'active'}
        )
        # If chat exists but is marked as JobDone, create a new one
        if not created and chat.status == 'job_done':
            chat = Chat.objects.create(
                user1=request.user if request.user.id < receiver.id else receiver,
                user2=receiver if request.user.id < receiver.id else request.user,
                status='active'
            )
    
    # Get all messages in this chat, ordered chronologically
    chat_messages = ChatMessage.objects.filter(chat=chat).order_by('timestamp')

    # Handle sending a new message
    if request.method == 'POST':
        content = request.POST.get('message')
        if content:
            # REF-005: Django ORM - create() method
            ChatMessage.objects.create(
                chat=chat,
                sender=request.user,
                receiver=receiver,
                content=content
            )
            # Create notification for the receiver
            # REF-028: ChatGPT - Notification creation for messages
            Notification.objects.create(
                user=receiver,
                notification_type='message',
                message=f'New message from {request.user.get_full_name() or request.user.username}',
                link=f'/chat/{request.user.username}/'
            )
            # Send email notification
            # REF-008: Django Email Backend - send_mail()
            try:
                if receiver.email:
                    send_mail(
                        subject=f'New Message from {request.user.get_full_name() or request.user.username}',
                        message=f'You have received a new message from {request.user.get_full_name() or request.user.username}.\n\nMessage: {content[:100]}{"..." if len(content) > 100 else ""}\n\nView the full conversation in your dashboard.',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[receiver.email],
                        fail_silently=True,
                    )
            except Exception:
                pass
            return redirect(f'/chat/{receiver.username}/')

    return render(request, 'chat/chat_detail.html', {
        'receiver': receiver,
        'chat': chat,
        'messages': chat_messages
    })


# Mark chat as JobDone when job is completed and verified
# REF-003: Django Views - Function-based views
# REF-005: Django ORM - get(), save()
# REF-006: Django Decorators - @login_required
# REF-007: Django Messages Framework
@login_required
def mark_chat_job_done(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    
    # Verify user is part of this chat
    if chat.user1 != request.user and chat.user2 != request.user:
        django_messages.error(request, "You don't have permission to modify this chat.")
        return redirect('chat_list')
    
    # Mark chat as JobDone
    chat.status = 'job_done'
    chat.completed_at = timezone.now()
    chat.save()
    
    django_messages.success(request, "Chat marked as Job Done. Future messages will start a new conversation.")
    return redirect('chat_list')

