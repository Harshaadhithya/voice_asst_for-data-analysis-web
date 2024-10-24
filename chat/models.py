import os
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from chat.constants import MESSAGE_TYPE_CHOICES


class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_chats')
    chat_title = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    @property
    def total_messages(self):
        return len(self.chat_messages.all())
    
    @property
    def total_attachments(self):
        return len(self.chat_attachments.all())
    
    @property
    def is_empty_chat(self):
        return (len(self.chat_messages.all())==0) and (len(self.chat_attachments.all())==0)
    
    @property
    def title(self):
        if self.chat_title:
            return self.chat_title
        attachments = self.chat_attachments.all()
        if attachments.count() == 1:
            # Return the single file's name without the path
            return os.path.basename(attachments[0].attachment_file.name)
        elif attachments.count() > 1:
            # Return first two file names joined by "-" without the path
            first_two_files = [os.path.basename(attachment.attachment_file.name) for attachment in attachments[:2]]
            return "-".join(first_two_files)
        return "No Title"

class ChatMessage(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='chat_messages')
    message_type = models.CharField(max_length=30, choices=MESSAGE_TYPE_CHOICES)
    message = models.TextField(null=True, blank=True)
    audio = models.FileField(upload_to='audio_output/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=['created_at']

    def save(self, *args, **kwargs):
        self.chat.updated_at = timezone.now()
        self.chat.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.chat.id}-{self.message_type}"


class ChatAttachment(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='chat_attachments')
    attachment_file = models.FileField(upload_to='chat_attachments/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.chat.id}"
    
    @property
    def file_name(self):
        if self.attachment_file and hasattr(self.attachment_file, 'name'):
            return os.path.basename(self.attachment_file.name)
        return None
