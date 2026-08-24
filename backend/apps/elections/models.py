from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.accounts.models import UserProfile, Program


class Party(models.Model):
    """Model for student political parties."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='party_logos/', blank=True, null=True)
    color = models.CharField(max_length=7, default='#0b6e3b', help_text="Hex color code for party branding")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'elections_party'
        ordering = ['name']
        verbose_name = 'Party'
        verbose_name_plural = 'Parties'


class SchoolPosition(models.Model):
    """Model for election positions."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    max_candidates = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'elections_schoolposition'
        ordering = ['display_order', 'name']
        verbose_name = 'School Position'
        verbose_name_plural = 'School Positions'


class SchoolElection(models.Model):
    """Model for election periods."""
    ELECTION_TYPE_CHOICES = [
        ('university', 'University Student Council (USC)'),
        ('department', 'Department Election'),
    ]

    title = models.CharField(max_length=200)
    election_type = models.CharField(
        max_length=20,
        choices=ELECTION_TYPE_CHOICES,
        default='university',
    )
    allowed_department = models.ForeignKey(
        Program,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'program_type': Program.ProgramType.DEPARTMENT},
        related_name='department_elections',
        to_field='code',
        help_text="Department allowed to vote (only for Department Election type)"
    )
    start_year = models.IntegerField(null=True, blank=True)
    end_year = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    is_paused = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_elections')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.start_year and self.end_year:
            if self.election_type == 'university':
                self.title = f"USC Election AY {self.start_year}-{self.end_year}"
            elif self.election_type == 'department' and self.allowed_department:
                self.title = f"{self.allowed_department.code} Election AY {self.start_year}-{self.end_year}"
            else:
                self.title = f"Election AY {self.start_year}-{self.end_year}"
        super().save(*args, **kwargs)

    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError("Start date must be before end date")

    def __str__(self):
        return self.title

    def is_active_now(self):
        now = timezone.now()
        return self.is_active and not self.is_paused and (self.start_date <= now <= self.end_date)

    def is_upcoming(self):
        now = timezone.now()
        return self.is_active and now < self.start_date

    def is_finished(self):
        now = timezone.now()
        return now > self.end_date

    def is_user_eligible(self, user):
        if self.election_type == 'university':
            return True
        if self.election_type == 'department':
            try:
                profile = user.profile
                return bool(self.allowed_department and profile.department and self.allowed_department.code == profile.department.code)
            except UserProfile.DoesNotExist:
                return False
        return False

    class Meta:
        db_table = 'elections_schoolelection'
        ordering = ['-start_date']
        verbose_name = 'School Election'
        verbose_name_plural = 'School Elections'


class ElectionPosition(models.Model):
    """Link elections with active positions."""
    election = models.ForeignKey(SchoolElection, on_delete=models.CASCADE, related_name='election_positions')
    position = models.ForeignKey(SchoolPosition, on_delete=models.CASCADE, related_name='position_elections')
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.election.title} - {self.position.name}"

    class Meta:
        db_table = 'elections_electionposition'
        unique_together = ['election', 'position']
        ordering = ['order', 'position__display_order']
        verbose_name = 'Election Position'
        verbose_name_plural = 'Election Positions'
