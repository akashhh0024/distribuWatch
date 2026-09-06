from django.db import models
from django.contrib.auth.hashers import check_password, make_password

# Create your models here.


class User(models.Model):

    email = models.EmailField(unique=True, null=False)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def __str__(self):
        return self.email
