from django.core.management.base import BaseCommand
from accounts.models import Profile

class Command(BaseCommand):
    help = 'Add initial balance to existing users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--amount',
            type=int,
            default=1000,
            help='Amount to add to each user\'s balance (default: 1000)'
        )

    def handle(self, *args, **options):
        amount = options['amount']
        
        # Get all profiles
        profiles = Profile.objects.all()
        
        for profile in profiles:
            profile.balance += amount
            profile.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Added {amount} MKD to {profile.user.username}\'s balance. New balance: {profile.balance} MKD'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully added {amount} MKD to {profiles.count()} users')
        )
