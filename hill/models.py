from django.db import models


class HillProgram(models.Model):
    author = models.ForeignKey("auth.User", on_delete=models.SET_NULL, blank=True, null=True) # don't delete the program if the author is deleted
    name = models.CharField(max_length=255) # name is author.name
    content = models.TextField() # the actual program; we don't point to it's corresponding SavedProgram because that could be changed or deleted, causing massive errors
    rank = models.IntegerField() # position on the hill
    prev_rank = models.IntegerField() # previous position on the hill
    points = models.IntegerField() # total sum of points earned
    score = models.IntegerField() # number determined by an algorithm

    def __str__(self):
        return self.name

class HillGame(models.Model): # the saved results of a game between two programs on the hill; this will eliminate the need to simulate a game between every program on the hill every time a new program is submitted
    left = models.ForeignKey("hill.HillProgram", on_delete=models.CASCADE, related_name="Left")
    right = models.ForeignKey("hill.HillProgram", on_delete=models.CASCADE, related_name="Right")
    points = models.IntegerField() # negative for left, positive for right
    games = models.TextField() # json; the results of each match

    def __str__(self):
        return f"{self.left} vs {self.right}"

    def getPoints(self, prog): # make sure the chosen program always gets + if won and - if lost, regardless of which side it's on
        if prog.pk == self.left.pk:
            return -1 * self.points
        else:
            return self.points
