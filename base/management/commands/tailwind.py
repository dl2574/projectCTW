from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.conf import settings

import subprocess

class Command(BaseCommand):
    help = "Initiate the tailwind css compiler."
    
    def add_arguments(self, parser):
        parser.add_argument(
            "-w", "--watch",
            action="store_true",
            help="Run in watch mode",
        )
        
    def handle(self, *args, **options):
        input_path = settings.TAILWIND_INPUT_FILE
        output_path = settings.TAILWIND_OUTPUT_FILE
        
        subprocess.call(["tailwindcss", "-i", input_path, "-o", output_path, "--watch" if options["watch"] else ""])
    
    
    