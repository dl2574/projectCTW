from django.core.management.base import BaseCommand
from django.core import management
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

        parser.add_argument(
            "-d", "--deploy",
            action="store_true",
            help="Minify tailwind and collect static"
        )

    def handle(self, *args, **options):
        input_path = settings.TAILWIND_INPUT_FILE
        output_path = settings.TAILWIND_OUTPUT_FILE

        # Build the command - always include -i so custom CSS in input.css is compiled
        cmd = ["tailwindcss", "-i", input_path, "-o", output_path]

        if options["watch"]:
            cmd.append("--watch")

        if options["deploy"]:
            # Minify in the same pass to avoid overwriting with a second CLI call
            cmd.append("--minify")

        subprocess.call(cmd)

        if options["deploy"]:
            management.call_command("collectstatic", "--no-input")
