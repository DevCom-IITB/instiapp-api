from uuid import uuid4

from django.db import models
from django.utils.timezone import now

STATUS = (
    ('reported', 'Reported'),
    ('in_progress', 'In Progress'),
    ('resolved', 'Resolved'),
    ('deleted', 'Deleted'),
)


class tag_uris(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    tag_uri = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Tag URI"
        verbose_name_plural = "Tag URIs"

    def __str__(self):
        return self.tag_uri


class complaints(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_by = models.ForeignKey('users.UserProfile',null=True, blank=True, on_delete=models.CASCADE, related_name="created_by")
    description = models.TextField(blank=True, null=True)
    report_date = models.DateTimeField(default=now)
    status = models.CharField(max_length=30, choices=STATUS, default='reported')
    latitude = models.FloatField(max_length=8, blank=True, null=True)
    longitude = models.FloatField(max_length=8, blank=True, null=True)
    location_description = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(tag_uris, related_name='tags', blank=True)
    users_up_voted = models.ManyToManyField('users.UserProfile', related_name='users_up_voted', blank=True)
    media = models.ManyToManyField('upload.UploadedImage', related_name='media', blank=True)

    ##
    class Meta:
        verbose_name = "Complaint"
        verbose_name_plural = "Complaints"

    def __str__(self):
        return self.description


class comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    time = models.DateTimeField(default=now)
    text = models.TextField()
    user = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE)
    complaint = models.ForeignKey(complaints, on_delete=models.CASCADE, related_name="comments")

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return self.text


        # class complaints_liked_users(models.Model):
        #     user = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE, related_name="liked_by")
        #     complaint = models.ForeignKey(complaints, on_delete=models.CASCADE)
        #
        #     class Meta:
        #         verbose_name = "Complaint liked by user"
        #         verbose_name_plural = "Complaint liked by users"
        #
        #     def __str__(self):
        #         return self.user.name
        #
        #
        # class complaint_tag_uris(models.Model):
        #     complaint = models.ForeignKey(complaints, on_delete=models.CASCADE)
        #     tags = models.ForeignKey(tag_uris, on_delete=models.CASCADE, related_name="Tags")
        #
        #     class Meta:
        #         verbose_name = "Complaint's tag"
        #         verbose_name_plural = "Complaint's tags"
        #
        #     def __str__(self):
        #         return self.tags.tag_uri
        #
        # class media_uris(models.Model):
        #     media = models.ForeignKey('upload.UploadedImage', on_delete=models.CASCADE, related_name='media', null=True, blank=True)
        #     complaint = models.ForeignKey(complaints, on_delete=models.CASCADE)
        #
        #     class Meta:
        #         verbose_name = "Media URI"
        #         verbose_name_plural = "Media URIs"
        #
        #     def __str__(self):
        #         return str(self.media.time_of_creation)

        # ============================Database Schema======================================
        #
        # CREATE TABLE IF NOT EXISTS complaints (
        #   id SERIAL PRIMARY KEY,
        #   rating VARCHAR(30),
        #   description VARCHAR(10000),
        #   report_date DATE,
        #   status VARCHAR(30),
        #   user_id INT NOT NULL,
        #   lat FLOAT(8),
        #   lon FLOAT(8),
        #   alt FLOAT(8),
        #   location_description VARCHAR(10000),
        #   users_liked INT[],
        #   comments INT[],
        #   FOREIGN KEY (user_id) REFERENCES users(id)
        # ) ;

        #
        # CREATE TABLE IF NOT EXISTS tag_uris (
        #   id SERIAL PRIMARY KEY,
        #   tag_uri VARCHAR(200)
        # );
        #
        # CREATE TABLE IF NOT EXISTS comment (
        #   id SERIAL PRIMARY KEY,
        #   time DATE,
        #   text VARCHAR(500),
        #   complaint_id INT NOT NULL,
        #   user_id INT NOT NULL
        # );
