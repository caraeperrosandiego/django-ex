from django.db import models

# Create your models here.

class Content(models.Model):
    url = models.CharField(max_length=2083, blank=False, default="")
    last_time_visited = models.DateTimeField(auto_now=True)
    shorter_url_name_service = models.CharField(max_length=32,
                                                blank=False,
                                                default="")

    # https://github.com/ellisonleao/pyshorteners/
    shortened_url = models.CharField(max_length=64,blank=False,
                                   default="", unique=True)


class Visit(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE, null=False)
    dt_visit = models.DateTimeField(auto_now_add=True)
    referer = models.CharField(max_length=2083,
                               blank=True,
                               default="")
    remote_ip = models.CharField(max_length=64, blank=False)
    remote_host = models.CharField(max_length=128, blank=False)
    http_agent = models.CharField(max_length=256, blank=False)
    country = models.CharField(max_length=32, blank=False, default="")
