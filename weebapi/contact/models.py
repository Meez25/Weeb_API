from django.db import models

from satisfaction.satisfaction import analyze_satisfaction


class Contact(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(20)
    email_address = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    satisfaction = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.message:
            self.satisfaction = analyze_satisfaction(self.message)
        super().save(*args, **kwargs)
