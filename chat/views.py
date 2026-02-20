# Chat functionality - allows customers and tradesmen to message each other
# Simple messaging system for discussing job details
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from .models import ChatMessage
from users.models import Notification
from django.core.mail import send_mail
from django.conf import settings


# Shows list of all people the user has chatted with
# Builds a list of unique chat partners from message history
# REF-003: Django Views - Function-based views
# REF-005: Django ORM - filter() and order_by()
# REF-006: Django Decorators - @login_required
# REF-010: Django Q Objects - OR condition (sender OR receiver)
# REF-018: Tom Dekan - Django chat app tutorial for messaging architecture
# REF-021: Django ORM - select_related() for query optimization
@login_required
def chat_list(request):
    # Get all messages where user is sender or receiver
    messages = ChatMessage.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).select_related('sender', 'receiver').order_by('-timestamp')

    # Build dictionary of unique chat partners
    chat_partners = {}
    for msg in messages:
        # Figure out who the other person is in each conversation
        partner = msg.receiver if msg.sender == request.user else msg.sender
        if partner.username not in chat_partners:
            chat_partners[partner.username] = partner

    return render(request, 'chat/chat_list.html', {'chat_partners': chat_partners.values()})


# Individual chat conversation view
# Shows all messages between current user and the specified user
# Also handles sending new messages
# REF-003: Django Views - Function-based views
# REF-005: Django ORM - filter() and order_by()
# REF-006: Django Decorators - @login_required
# REF-010: Django Q Objects - OR condition for bidirectional messages
# REF-018: Tom Dekan - Django chat app tutorial
@login_required
def chat_detail(request, username):
    receiver = User.objects.get(username=username)
    # Get all messages between these two users, ordered chronologically
    # REF-010: Django Q Objects - OR condition for bidirectional message retrieval
    messages = ChatMessage.objects.filter(
        Q(sender=request.user, receiver=receiver) |
        Q(sender=receiver, receiver=request.user)
    ).order_by('timestamp')

    # Handle sending a new message
    if request.method == 'POST':
        content = request.POST.get('message')
        if content:
            # REF-005: Django ORM - create() method
            ChatMessage.objects.create(sender=request.user, receiver=receiver, content=content)
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
        'messages': messages
    })

