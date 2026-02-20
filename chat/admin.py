from django.contrib import admin
from .models import Chat, ChatMessage

# REF-001: Django Admin - ModelAdmin class
@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'user1', 'user2', 'status', 'created_at', 'completed_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user1__username', 'user2__username')
    readonly_fields = ('created_at', 'completed_at')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'sender', 'receiver', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('sender__username', 'receiver__username', 'content')
    readonly_fields = ('timestamp',)
