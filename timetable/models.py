from django.db import models
class AdminLogin(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.email