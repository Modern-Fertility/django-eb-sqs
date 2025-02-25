from __future__ import absolute_import, unicode_literals

from django.urls import re_path

from eb_sqs.views import process_task

urlpatterns = [
    re_path(r"^process$", process_task, name="process_task"),
]
