from django.db import models

class SavedProgram(models.Model):
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=96)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    content = models.TextField()
    private = models.BooleanField()

    def __str__(self):
        return f"{self.author}.{self.name}"