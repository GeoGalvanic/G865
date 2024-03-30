from django.contrib.gis.db import models
from django.contrib.auth.models import User


# Create your models here.
class QueueEntry(models.Model):
    name = models.CharField(max_length = 100)
    upload_file_name = models.CharField(max_length = 255)
    buffer_string = models.CharField(max_length = 100, null = True, blank = True)
    number_features = models.IntegerField(null = True, blank = True)
    number_buffers = models.IntegerField(null = True, blank = True)
    #gp_type = models.CharField(max_length = 64)
    creator_user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = 'QueueTasks',
    )
    start_time = models.DateTimeField(null = True)
    output_file = models.FileField(upload_to = 'uploads', null = True, blank = True)
    complete = models.BooleanField(default = False)

class Buff(models.Model):
    fake_id = models.BigAutoField(primary_key=True)
    Group_ID = models.IntegerField()
    Feat_ID = models.IntegerField()
    Buffer_Size = models.IntegerField()
    Shape = models.PolygonField()


