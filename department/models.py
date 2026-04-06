from django.db import models

class Department(models.Model):
    TYPE_CHOICES = (
        (1, 'School'),
        (2, 'College'),
    )

    name = models.CharField(max_length=100)
    type = models.IntegerField(choices=TYPE_CHOICES)

    def __str__(self):
        return self.name