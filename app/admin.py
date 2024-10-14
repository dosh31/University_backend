from django.contrib import admin

from .models import *

admin.site.register(Specialist)
admin.site.register(Lecture)
admin.site.register(SpecialistLecture)
