from django.db import models
from django.contrib.auth.models import User
import uuid
from django.shortcuts import reverse
from django.template.defaultfilters import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    unique_link = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


CURRENCY_CHOICES = [
    ('CAD', 'CAD'),
    ('USD', 'USD'),
    ('EUR', 'EUR'),
    ('RUB', 'RUB'),
    ('KZT', 'KZT')
]


class MoneyBlock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.balance} {self.currency} {self.created_at}"


class Transaction(models.Model):
    money_block = models.ForeignKey(MoneyBlock, on_delete=models.CASCADE, related_name='transactions')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.description}, {self.amount}, {self.date}"
