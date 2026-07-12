from django.db import models

class PlacementCompanyThread(models.Model):
    company_name    = models.CharField(max_length=200)
    company_slug    = models.SlugField(db_index=True)
    first_post_date = models.DateTimeField(db_index=True)

    # Enriched from the IAF Open post — filled when IAF Open is ingested
    category        = models.CharField(max_length=10, blank=True)  # I1 / I2 / I3 / I4 / W1 / W2
    role            = models.TextField(blank=True)                  # comma-separated if multiple profiles
    domain          = models.CharField(max_length=200, blank=True)

    bonus_jaf       = models.CharField(max_length=100, blank=True)
    cpi_cutoff      = models.TextField(blank=True)
    bond            = models.CharField(max_length=255, null=True, blank=True)
    mode            = models.CharField(max_length=255, null=True, blank=True)
    
    jaf_deadline    = models.DateTimeField(null=True, blank=True)

    # Sets default ordering to show newest threads first
    class Meta:
        ordering = ['-first_post_date']

    # Defines how the object is displayed
    def __str__(self):
        return f"{self.company_name} Thread ({self.first_post_date.date()})"


class PlacementBlogPost(models.Model):
    POST_TYPES = [
        ('JAF_OPEN',              'JAF Open'),
        ('TEST',                  'Test'),
        ('TEST_SHORTLIST',        'Test Shortlist'),
        ('TEST_UPDATE',           'Test Update'),
        ('ASSIGNMENT_DETAILS',    'Assignment Details'),
        ('ASSIGNMENT_SHORTLIST',  'Assignment Shortlist'),
        ('MANDATORY_FORM',        'Mandatory Form'),
        ('INTERVIEW_SHORTLIST',   'Interview Shortlist'),
        ('INTERVIEW_SCHEDULE',    'Interview Schedule'),
        ('INTERVIEW_UPDATE',      'Interview Update'),
        ('GD_SCHEDULE',           'GD Schedule'),
        ('GD_UPDATE',             'GD Update'),
        ('ROUND2_SHORTLIST',      'Round 2 Shortlist'),
        ('FINAL_SELECTION',       'Final Selection'),
        ('OTHER',                 'Other'),
    ]

    # Uses the UUID directly from the JSON feed to prevent duplicates
    id               = models.UUIDField(primary_key=True)           # from source, do not auto-generate
    thread           = models.ForeignKey(
                           PlacementCompanyThread, null=True, blank=True,
                           on_delete=models.SET_NULL,
                           related_name='posts')
    post_type        = models.CharField(max_length=30, choices=POST_TYPES)
    raw_company_name = models.CharField(max_length=200)             # before normalization
    published        = models.DateTimeField(db_index=True)
    raw_content      = models.TextField()
    link             = models.URLField()
    pinned           = models.BooleanField(default=False)

    # Sorts posts chronologically inside a thread
    class Meta:
        ordering = ['published']
    
    def __str__(self):
        return f"{self.raw_company_name} - {self.get_post_type_display()}"


class PlacementExtractedData(models.Model):
    post               = models.OneToOneField(
                             PlacementBlogPost, on_delete=models.CASCADE,
                             related_name='extracted')

    # Fields present in IAF Open posts
    category           = models.CharField(max_length=10, blank=True)
    role               = models.TextField(blank=True)       # comma-separated
    domain             = models.CharField(max_length=200, blank=True)

    bonus_jaf          = models.CharField(max_length=100, blank=True)
    cpi_cutoff         = models.TextField(blank=True)
    bond               = models.CharField(max_length=255, null=True, blank=True)
    mode               = models.CharField(max_length=255, null=True, blank=True)
    
    deadline           = models.DateTimeField(null=True, blank=True)
    shortlisted_rolls  = models.JSONField(default=list, blank=True, null=True)
    event_date         = models.DateTimeField(null=True, blank=True)
    venue              = models.CharField(max_length=300, blank=True)

    time               = models.CharField(max_length=50, blank=True) 
    
    placement_slots    = models.JSONField(default=list, blank=True, null=True)

    def __str__(self):
        return f"Data for {self.post.id}"