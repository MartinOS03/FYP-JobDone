# Generated migration for Chat model and ChatMessage.chat field
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def migrate_existing_messages(apps, schema_editor):
    """Migrate existing ChatMessages to Chat model"""
    Chat = apps.get_model('chat', 'Chat')
    ChatMessage = apps.get_model('chat', 'ChatMessage')
    User = apps.get_model(settings.AUTH_USER_MODEL)
    
    # Group messages by sender/receiver pairs
    message_pairs = {}
    for msg in ChatMessage.objects.all():
        # Create a consistent key (smaller ID first)
        user1_id = min(msg.sender_id, msg.receiver_id)
        user2_id = max(msg.sender_id, msg.receiver_id)
        key = (user1_id, user2_id)
        
        if key not in message_pairs:
            message_pairs[key] = []
        message_pairs[key].append(msg)
    
    # Create Chat for each pair and assign messages
    for (user1_id, user2_id), messages in message_pairs.items():
        user1 = User.objects.get(id=user1_id)
        user2 = User.objects.get(id=user2_id)
        
        # Create or get chat
        chat, created = Chat.objects.get_or_create(
            user1=user1,
            user2=user2,
            defaults={'status': 'active'}
        )
        
        # Update all messages to belong to this chat
        for msg in messages:
            msg.chat = chat
            msg.save()


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_rename_message_chatmessage'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('active', 'Active'), ('job_done', 'Job Done')], default='active', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('user1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chats_as_user1', to=settings.AUTH_USER_MODEL)),
                ('user2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chats_as_user2', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='chat',
            index=models.Index(fields=['user1', 'user2', 'status'], name='chat_chat_user1_i_70c9a6_idx'),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='chat',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.chat'),
        ),
        migrations.RunPython(
            code=migrate_existing_messages,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='chat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.chat'),
        ),
    ]
