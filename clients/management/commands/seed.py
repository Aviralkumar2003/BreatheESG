from django.core.management.base import BaseCommand
from faker import Faker
from clients.models import Client


class Command(BaseCommand):
    help = 'Seed the database with initial clients'

    def handle(self, *args, **kwargs):
        fake = Faker()
        self.stdout.write('Seeding database...')

        clients = [
            'Acme Corp',
            'Globex Corporation',
            'Stark Industries',
        ]

        for client_name in clients:
            client, created = Client.objects.get_or_create(
                name=client_name,
                defaults={
                    'plant_code_map': {
                        '1000': fake.city(),
                        '2000': fake.city(),
                        '3000': fake.city(),
                    }
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created client: {client.name}'))
            else:
                self.stdout.write(f'  Client already exists: {client.name}')

        self.stdout.write(self.style.SUCCESS('Seeding complete.'))
