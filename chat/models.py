# Chat message model - stores messages between users
# Used for customers and tradesmen to communicate about jobs
# REF-001: Django Models Documentation - Model definition
# REF-018: - Django chat app tutorial for messaging architecture
from django.db import models
from django.contrib.auth.models import User

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']  # Oldest messages first (for chat display)

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username}: {self.content[:20]}"
