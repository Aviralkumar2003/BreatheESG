import os
import django
from faker import Faker

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from clients.models import Client

def run_seed():
    fake = Faker()
    print("Seeding database...")
    
    clients = [
        "Acme Corp",
        "Globex Corporation",
        "Stark Industries"
    ]
    
    for client_name in clients:
        client, created = Client.objects.get_or_create(
            name=client_name,
            defaults={
                'plant_code_map': {
                    "1000": fake.city(),
                    "2000": fake.city(),
                    "3000": fake.city()
                }
            }
        )
        if created:
            print(f"Created client: {client.name}")
        else:
            print(f"Client already exists: {client.name}")

    print("Seeding complete.")

if __name__ == '__main__':
    run_seed()
