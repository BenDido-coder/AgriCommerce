from django.contrib.auth.management.commands.createsuperuser import Command as BaseCommand
from django.core.management import CommandError
from ac.models import User

class Command(BaseCommand):
    help = 'Create a superuser with custom fields'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--phone', type=str, help='User phone number')
        parser.add_argument('--user_type', type=str, help='User type')

    def handle(self, *args, **options):
        phone = options.get('phone')
        user_type = options.get('user_type')

        if not phone or not user_type:
            raise CommandError('--phone and --user_type are required')

        user_data = {
            'email': options['email'],
            'phone': phone,
            'user_type': user_type.upper(),
            'is_staff': True,
            'is_superuser': True
        }

        User.objects.create_superuser(**user_data)
        self.stdout.write(self.style.SUCCESS('Superuser created successfully'))