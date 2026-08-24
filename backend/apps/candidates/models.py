from django.db import models
from django.contrib.auth.models import User
from apps.elections.models import SchoolPosition, SchoolElection, Party
from apps.common.files.upload_paths import candidate_photo_upload_path


class Candidate(models.Model):
    """Model for approved candidates running for school election positions."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='candidates')
    position = models.ForeignKey(SchoolPosition, on_delete=models.CASCADE, related_name='candidates')
    election = models.ForeignKey(SchoolElection, on_delete=models.CASCADE, related_name='candidates')
    party = models.ForeignKey(Party, on_delete=models.SET_NULL, null=True, blank=True, related_name='candidates')
    manifesto = models.TextField(blank=True, help_text="Campaign manifesto and goals")
    photo = models.ImageField(upload_to=candidate_photo_upload_path, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position.name} ({self.election.title})"

    class Meta:
        db_table = 'candidates_candidate'
        ordering = ['position__display_order', 'user__first_name']
        unique_together = ['user', 'election', 'position']
        verbose_name = 'Candidate'
        verbose_name_plural = 'Candidates'
