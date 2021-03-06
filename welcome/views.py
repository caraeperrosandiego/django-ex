import os
import traceback
from django.shortcuts import render
#from django.conf import settings
#from django.http import HttpResponse

from . import database
from .models import Content, Visit

from django.db import transaction
from .AdflyAPI import AdflyApi
#from django.http import Http404
from django.http import HttpResponseNotFound

from geolite2 import geolite2
# import pprint


def publish(request):
    WITHOUT_ADVERTISING = 0
    WITH_ADVERTISING = 1
    BOTH_IN_TWO_WINDOWS = 2

    shorter_url_name_service = request.GET.get('suns', "")

    shortened_url_protocol = request.GET.get('ptc', "")
    shortened_url_netloc = request.GET.get('nl', "")
    shortened_url_path = request.GET.get('pth', "")

    shortened_url = shortened_url_protocol+"://"+shortened_url_netloc+shortened_url_path

    # publication_mode = int(request.GET.get('pm', "2"))
    publication_mode = request.GET.get('pm', "2")

    reader = geolite2.reader()
    remote_ip = request.META.get('HTTP_X_FORWARDED_FOR', "")
    result = reader.get(remote_ip)
    if result:
        country = result['country']['names']['es']
    else:
        country = "N/A"
    geolite2.close()

        # pp = pprint.PrettyPrinter(indent=4)
    # print("\nMeta:\n")
    # pp.pprint(request.META)
        # print("\n\nResul:\n")
        # pp.pprint(result)

    content = None

    try:
        content = Content.objects.get(shortened_url=shortened_url)

        with transaction.atomic():
            # Se actualiza el atributo last_time_visited al ejecutar .save()
            content.save()
            visit = Visit.objects.create(content=content,
                                         referer=request.META.get('HTTP_REFERER', ""),
                                         remote_ip=request.META.get('HTTP_X_FORWARDED_FOR', ""),
                                         # remote_host=request.META.get('REMOTE_HOST', ""),
                                         remote_host=request.META.get('HTTP_FORWARDED', ""),
                                         http_agent=request.META.get('HTTP_USER_AGENT', ""),
                                         country=country)

    except Content.DoesNotExist:
        with transaction.atomic():

            adfly_api = AdflyApi()
            result = adfly_api.expand(shortened_url)
            original_url = result['data'][0]['url']
            # url_request = urls.reverse('publish')


            content = Content.objects.create(url=original_url,
                                         shorter_url_name_service=shorter_url_name_service,
                                         shortened_url=shortened_url)

            visit = Visit.objects.create(content=content,
                                         referer=request.META.get('HTTP_REFERER', ""),
                                         remote_ip=request.META.get(
                                             'HTTP_X_FORWARDED_FOR', ""),
                                         remote_host=request.META.get(
                                             'HTTP_FORWARDED', ""),
                                         http_agent=request.META.get('HTTP_USER_AGENT', ""),
                                         country=country)

    except Exception as e:
        print("Error en view: " + str(e))
        print("||||||||||||||||||||||||||||||||||||||||||||||||||||\n")
        print(traceback.format_exc())
        # raise Http404("Houston!, we have a problem...")

        # https://overiq.com/django/1.10/showing-404-errors-in-django/
        return HttpResponseNotFound("Houston!, we have a problem...")



    visits = Visit.objects.filter(content=content).count()

    if visits > 5:
        return render(request, 'welcome/publish.html', {
            'inspection_facebook_time':False,
            'publication_mode':publication_mode,
            'content':content
        })

    else:
        return render(request, 'welcome/publish.html', {
            'inspection_facebook_time':True,
            'content': content
        })




def index(request):
    hostname = os.getenv('HOSTNAME', 'unknown')

    return render(request, 'welcome/index.html', {
        'hostname': hostname,
        'database': database.info()
    })



# MaxMind GeoLite2 database as a convenient Python package
#   https://github.com/rr2do2/maxminddb-geolite2

###