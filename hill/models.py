from django.db import models


class HillProgram(models.Model):
    author = models.ForeignKey("auth.User", on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=255)
    content = models.TextField()
    rank = models.IntegerField() # position on the hill
    prev_rank = models.IntegerField()
    points = models.IntegerField() # total sum of points earned
    score = models.IntegerField() # number determined by an algorithm

    def __str__(self):
        return self.name

class HillGame(models.Model):
    left = models.ForeignKey("hill.HillProgram", on_delete=models.CASCADE, related_name="Left")
    right = models.ForeignKey("hill.HillProgram", on_delete=models.CASCADE, related_name="Right")
    points = models.IntegerField()
    games = models.TextField() # json

    def __str__(self):
        return f"{self.left} vs {self.right}"

    def getPoints(self, prog): # make sure the chosen program always gets + if won and - if lost, regardless of which side it's on
        if prog.pk == self.left.pk:
            return -1 * self.points
        else:
            return self.points
