# Chat message model - stores messages between users
# Used for customers and tradesmen to communicate about jobs
# REF-001: Django Models Documentation - Model definition
# REF-018: - Django chat app tutorial for messaging architecture
from django.db import models
from django.contrib.auth.models import User


# Chat conversation model - represents a conversation between two users
# When a job is completed and verified, the chat is marked as "JobDone"
# Future messages between the same users create a new chat
# REF-001: Django Models Documentation - Model definition with choices field
class Chat(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('job_done', 'Job Done'),
    ]
    
    user1 = models.ForeignKey(User, related_name='chats_as_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='chats_as_user2', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        # Ensure we can query chats efficiently
        indexes = [
            models.Index(fields=['user1', 'user2', 'status']),
        ]
    
    def __str__(self):
        return f"Chat: {self.user1.username} ↔ {self.user2.username} ({self.status})"
    
    def get_other_user(self, current_user):
        """Helper to get the other user in the chat"""
        return self.user2 if self.user1 == current_user else self.user1


class ChatMessage(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']  # Oldest messages first (for chat display)

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username}: {self.content[:20]}"
