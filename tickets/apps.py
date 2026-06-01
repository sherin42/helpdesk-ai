import os
from django.apps import AppConfig


class TicketsConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'

    name = 'tickets'

    def ready(self):

        if os.environ.get('RUN_MAIN') == 'true':

            from .scheduler import start_scheduler

            start_scheduler()