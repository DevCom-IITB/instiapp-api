from django.db import models

# Create your models here.
class PopUp(models.Model):
    heading = models.CharField(max_length=100, verbose_name="Alert Title", blank=True, default='Title')
    short_description = models.CharField(max_length=200, verbose_name="short description", blank=True)
    long_description = models.TextField(verbose_name="long description", blank=True)
    image_url = models.URLField(max_length=500, verbose_name="image link", blank=True)
    links = models.JSONField(default=list, verbose_name="Add links", blank=True, null=True)
    is_active = models.BooleanField(default=True, help_text="Controls whether this popup is currently being served to users.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.heading or "Untitled Pop-up"

    class Meta:
        db_table = 'pop_up'
        verbose_name = "Pop-up Notification"
        verbose_name_plural = "Pop-up Notifications"
        ordering = ['-created_at']


class UserPopUpRead(models.Model):
    user = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE)
    popup = models.ForeignKey(PopUp, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'popup_notification_read_status'
        unique_together = ('user', 'popup')
