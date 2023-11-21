from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Creates a user"

    def add_arguments(self, parser):
        parser.add_argument("-u", "--username", type=str)

    def handle(self, *args, **options):
        print(args.username)
        username = args.username.replace('@', '___at___')
        print(username)
        # user = get_user_model().objects.create_user(username='{username}')