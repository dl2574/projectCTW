from django.core.management.base import BaseCommand
from django.core.management.utils import get_random_secret_key
from django.conf import settings
import os


class Command(BaseCommand):
    help = "Sets a new SECRET_KEY within the .env file."

    def handle(self, *args, **kwargs):
        # Filepath to the .env file in the base project directory
        file_path = os.path.join(settings.BASE_DIR, ".env")
        data_dict = {}

        # Attempt to open the file and read the lines. If the file does not exist set the DEBUG value to be added
        # into the newly created file.
        try:
            with open(file_path, "r") as file:
                data_list = file.readlines()

                # Split the list of lines into a dictionary key value pairs for each variable in the file
                data_dict = {item.split("=")[0]: item.split("=")[1] for item in data_list}

        # If the file does not exist, add the DEBUG variable pair
        except FileNotFoundError:
            data_dict["DEBUG"] = "True\n"


        # Generate a new random secret key and add a new line character to the end of it
        new_key_entry = str(get_random_secret_key()) + "\n"

        # Update the SECRET_KEY value in the data dictionary
        data_dict["SECRET_KEY"] = new_key_entry

        # Complie the data dictionary back into a list of strings for writing back into the file
        new_data_list = [item[0] + "=" + item[1] for item in data_dict.items()]

        with open(file_path, "w") as file:
            file.writelines(new_data_list)