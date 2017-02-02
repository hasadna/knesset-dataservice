import logging


class BaseScraper(object):

    def __init__(self, logger=None):
        self.logger = logging.getLogger(self.__module__) if not logger else logger
