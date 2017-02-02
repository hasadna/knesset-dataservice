from django.core.management.base import NoArgsCommand
import logging
from django.conf import settings
import sys


class BaseNoArgsCommand(NoArgsCommand):
    """
    root class for management commands

    all extending classes must call super class handle_noargs

    provides common functionality:

    * logging
        * when running this management command all existing django loggers will be removed (configurable)
        * they will be replaced with single logger to stdout
        * also, additional loggers can be added (for example, to track scrapers progress / status)
    """

    def __init__(self):
        super(BaseNoArgsCommand, self).__init__()
        self.command_name = "{app_name}.{command_name}".format(app_name=self.__module__.split('.')[-4],
                                                               command_name=self.__module__.split('.')[-1])
        self.logger = logging.getLogger(self.__module__)
        if getattr(settings, 'KNESSET_DATA_DJANGO_RESET_LOGGERS', True):
            [logging.root.removeHandler(handler) for handler in tuple(logging.root.handlers)]
            self.stdout_handler = logging.StreamHandler(sys.stdout)
            self.stdout_handler.setFormatter(logging.Formatter("%(name)s:%(lineno)d\t%(levelname)s\t%(message)s"))
            self.stdout_handler.setLevel(logging.DEBUG)
            logging.root.addHandler(self.stdout_handler)
            logging.root.setLevel(logging.DEBUG)
        else:
            self.stdout_handler = None

    def handle_noargs(self, **options):
        if self.stdout_handler:
            self.stdout_handler.setLevel({"3": logging.DEBUG,
                                          "2": logging.INFO,
                                          "1": logging.WARN,
                                          "0": logging.ERROR}[options.get('verbosity', '1')])
