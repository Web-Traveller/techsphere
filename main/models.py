# main/models.py #}
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.crypto import get_random_string

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']

    groups = models.ManyToManyField(
        Group,
        verbose_name=('groups'),
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="techsphere_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=('user permissions'),
        blank=True,
        help_text=('Specific permissions for this user.'),
        related_name="techsphere_user_perm_set",
        related_query_name="user",
    )

    def __str__(self):
        return self.email

class Team(models.Model):
    team_leader = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='led_teams')
    name = models.CharField(max_length=200)
    team_id = models.CharField(max_length=20, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    competition = models.ForeignKey('Competition', on_delete=models.CASCADE, related_name='teams')

    def save(self, *args, **kwargs):
        if not self.team_id:
            last_team = Team.objects.order_by('-id').first()
            if last_team:
                last_id = int(last_team.team_id[3:])
                new_id = last_id + 1;
                self.team_id = f"TST{new_id:03d}";
            else:
                self.team_id = "TST001"
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.name} ({self.team_id})"

class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members_details')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    branch = models.CharField(max_length=100, blank=True, null=True)
    year = models.CharField(max_length=20, blank=True, null=True)
    college_name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name

class Competition(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    rules = models.TextField(blank=True, null=True)
    prize = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='competition_images/', blank=True, null=True)
    rulebook_link = models.URLField(max_length=500, blank=True, null=True)
    coordinator_details = models.TextField(blank=True, null=True)
    max_team_size = models.PositiveIntegerField(default=4)
    is_individual = models.BooleanField(default=False)
    payment_qr_code = models.ImageField(upload_to='competition_qr_codes/', blank=True, null=True)

    def __str__(self):
        return self.name

class TeamCompetitionRegistration(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    registration_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid_not_verified', 'Paid Not Verified'),
        ('paid_verified', 'Paid Verified'),
    ]

    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_screenshot = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)
    transaction_number = models.CharField(max_length=200, blank=True, null=True)
    participant_details = models.JSONField(blank=True, null=True)

    def __str__(self):
        if self.team:
           return f"{self.team} - {self.competition}"
        else :
            return f"{self.user} - {self.competition}"

class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('read', 'Read'),
    ]
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unread')

    def __str__(self):
        return f"{self.name} - {self.email}"