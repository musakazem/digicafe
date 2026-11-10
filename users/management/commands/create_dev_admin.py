from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from users.models import AdminProfile, User

DEFAULT_EMAIL = 'admin@digicafe.test'
DEFAULT_PASSWORD = 'digicafe-admin'


class Command(BaseCommand):
    help = 'Create (or reset) a development admin account. Only runs when DEBUG is on.'

    def add_arguments(self, parser):
        parser.add_argument('--email', default=DEFAULT_EMAIL)
        parser.add_argument('--password', default=DEFAULT_PASSWORD)
        parser.add_argument('--name', default='Demo Admin')

    @transaction.atomic
    def handle(self, *args, email, password, name, **options):
        if not settings.DEBUG:
            raise CommandError('Refusing to create a development admin while DEBUG is off.')

        email = email.strip().lower()
        user, created = User.objects.get_or_create(
            email=email,
            defaults={'full_name': name, 'role': User.Role.ADMIN},
        )
        user.full_name = name
        user.role = User.Role.ADMIN
        user.is_active = True
        user.is_staff = True  # can also use the Django admin site at /admin/
        user.is_superuser = True
        user.set_password(password)
        user.save()
        AdminProfile.objects.get_or_create(user=user, defaults={'employee_id': 'DEV-ADMIN'})

        action = 'Created' if created else 'Reset'
        self.stdout.write(self.style.SUCCESS(f'{action} development admin: {email} / {password}'))
