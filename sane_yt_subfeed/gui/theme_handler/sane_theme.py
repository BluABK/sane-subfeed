import json
import os

from PyQt5.QtCore import QObject

KEYS_WANTED = ['name', 'version', 'author', 'description', 'compiled_qrc', 'variants']


class SaneTheme(QObject):

    def __init__(self, theme_dir_absolute_path, theme_handler=None):
        """
        Creates a custom theme from relevant files and returns it as a dict

        metadata.json specification:
        {
          "name": "<name>",
          "version": "<version>",
          "author": "<author>",
          "description": "<description>",
          "compiled_qrc": "resources.py",
          "variants":
          [
            {
              "name": "<name of variant 1>",
              "filename": "<filename of variant 1>.qss"
              "platform_whitelist": <null or list containing linux|win32|cygwin|darwin>
            },
            {
              "name": "<name of variant 2>",
              "filename": "<filename of variant 2>.qss"
              "platform_whitelist": <null or list containing linux|win32|cygwin|darwin>
            }, ....
          ]
        }

        :param: theme_dir_absolute_path:    Full path to the theme directory (in the themes directory).
        :param: theme_handler:              Pointer to theme handler in order to send things up the chain.
        :return:
        """
        super(SaneTheme).__init__()

        self.theme_handler = theme_handler

        self.name = None
        self.version = None
        self.author = None
        self.description = None
        self.theme_dir_absolute_path = theme_dir_absolute_path
        self.compiled_qrc_filename = None
        self.compiled_qrc_modulename = None

        # A list of files in the theme directory
        self.files = []

        # List of dict per variant.
        self.variants = []

        # Contains any additional data that isn't pertinent to a theme.
        self.extraneous_data = None

        # Locate and store a list of all the files in the theme directory.
        self.locate_files()

        # Create self given absolute path to its theme directory.
        self.create()

    def locate_files(self):
        # Empty the current list of files to avoid dupes.
        self.files = []

        # Iterate through the files in the theme directory.
        for file in os.listdir(self.theme_dir_absolute_path):
            # Only care about files, directories are irrelevant from this scope.
            if os.path.isfile(os.path.join(self.theme_dir_absolute_path, file)):
                self.files.append(file)

    def locate_compiled_qrc_module(self):
        for file in self.files:
            # Store info about any required compiled qrc file (basic guess by name, best if user specifies in JSON.
            if file.endswith('.py') and 'resources' in file:
                self.compiled_qrc_filename = file
            else:
                self.compiled_qrc_filename = None

    def post_process_variants(self):
        """
        Applies any necessary post-processing to the list of variants.
        :return:
        """
        # Convert variant filename paths to absolute paths:
        for variant in self.variants:
            variant['file_absolute_path'] = os.path.join(self.theme_dir_absolute_path, variant['filename'])

    def create_from_json(self):
        """
        Parse metadata from nice and tidy sensible JSON.
        :return:
        """
        with open(os.path.join(self.theme_dir_absolute_path, 'metadata.json'), 'r') as infile:
            # Read metadata.json directly into a metadata dict
            # FIXME: Turn into defaultDict or otherwise handling of non-existent keys
            metadata = json.load(infile)

            # Assign values to self based on metadata dict.
            self.name = metadata['name']
            self.version = metadata['version']
            self.author = metadata['author']
            self.description = metadata['description']
            self.variants = metadata['variants']

            if 'compiled_qrc' not in metadata:
                self.locate_compiled_qrc_module()
            else:
                self.compiled_qrc_filename = metadata['compiled_qrc']

            # Remove expected keys from metadata and store any extraneous data.
            for k in KEYS_WANTED:
                if k in metadata:
                    metadata.pop(k)
            self.extraneous_data = metadata

    def create_from_best_guess(self):
        """
        Make rudimentary best guesses based on filenames.
        :return:
        """
        for file in self.files:
            if file.endswith('.qss'):
                variant_path = file
                variant_name, sep, extension = file.partition('.qss')

                # Add variant to list of variants.
                self.variants.append({'name': variant_name, 'filename': os.path.join(self.theme_dir_absolute_path, variant_path),
                                      'platform_whitelist': None})

        # Assign theme values based on best guess.
        self.name = os.path.split(self.theme_dir_absolute_path)[-1]

        self.locate_compiled_qrc_module()

    def create(self):
        # Parse metadata json (if one exists), if not make best guesses based on filenames.
        if 'metadata.json' in self.files:
            self.create_from_json()
        else:
            self.create_from_best_guess()

        # Post-process variants
        self.post_process_variants()

        # Compiled QRC handling: Partition out the file extension (for module loading), if it exists.
        if self.compiled_qrc_filename:
            self.compiled_qrc_modulename, sep, junk = self.compiled_qrc_filename.partition('.py')
