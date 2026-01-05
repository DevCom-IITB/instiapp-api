from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import PollVote, PollOption

@receiver([post_save, post_delete], sender=PollVote)
def update_poll_option_vote_count(sender, instance, **kwargs):
    """
    Listens for a vote being saved or deleted, then updates the
    vote_count on the related PollOption.
    """
    try:
        option = instance.option
        # Recalculate the vote count from the database for 100% accuracy
        option.vote_count = option.votes.count()
        option.save(update_fields=['vote_count'])
    except PollOption.DoesNotExist:
        pass