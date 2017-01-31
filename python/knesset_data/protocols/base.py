# -*- coding: utf-8 -*-
from urllib2 import urlopen
import contextlib
from tempfile import mkstemp
import os
from utils import antiword, antixml
from cached_property import cached_property
import requests
import io


class BaseProtocolFile(object):

    temp_file_suffix = "temp_knesset_data_protocols_"

    def __init__(self, file, proxies=None):
        self._file_type, self._file_data = file
        self._cleanup = []
        self._proxies = proxies if proxies else {}

    def _get_file_from_url(self, url):
        # allows to modify the url opening in extending classes
        # when doing so, remember to use the proxies to route traffic through the given socks proxies
        return io.BytesIO(requests.get(url, proxies=self._proxies).content)

    @cached_property
    def file(self):
        if self._file_type == 'url':
            return self._get_file_from_url(self._file_data)
        elif self._file_type == 'filename':
            return open(self._file_data)
        elif self._file_type == 'file':
            return self._file_data
        elif self._file_type == 'data':
            return open(self.file_name)
        else:
            raise NotImplementedError('file type %s is not supported'%self._file_type)

    @cached_property
    def file_extension(self):
        if self._file_type in ("filename", "url") and self._file_data:
            filename, file_extension = os.path.splitext(self._file_data)
            return file_extension[1:]
        else:
            return None

    @cached_property
    def file_name(self):
        if self._file_type == 'filename':
            return self._file_data
        else:
            suffix = ".%s"%self.file_extension if self.file_extension is not None else ""
            fid, fname = mkstemp(suffix=suffix, prefix=self.temp_file_suffix)
            f = open(fname, 'wb')
            f.write(self.file_contents)
            f.close()
            self._cleanup.append(lambda: os.remove(fname))
            return fname

    @cached_property
    def file_contents(self):
        if self._file_type == 'data':
            return self._file_data
        else:
            return self.file.read()

    @cached_property
    def antiword_xml(self):
        return antiword(self.file_name)

    @cached_property
    def antiword_text(self):
        return antixml(self.antiword_xml)

    def _close(self):
        [func() for func in self._cleanup]

    @classmethod
    @contextlib.contextmanager
    def _get_from(cls, file_type, file_data, proxies=None):
        obj = cls((file_type, file_data), proxies=proxies)
        try:
            yield obj
        finally:
            if os.environ.get('KNESSET_DATA_PROTOCOLS_KEEP_FILES', None) == "yes":
                print "\n"
                print "keeping file: %s"%obj.file_name
                print "\n"
            else:
                obj._close()

    @classmethod
    @contextlib.contextmanager
    def get_from_url(cls, url, proxies=None):
        with cls._get_from('url', url, proxies=proxies) as p: yield p

    @classmethod
    @contextlib.contextmanager
    def get_from_file(cls, file):
        with cls._get_from('file', file) as p: yield p

    @classmethod
    @contextlib.contextmanager
    def get_from_filename(cls, filename):
        with cls._get_from('filename', filename) as p: yield p

    @classmethod
    @contextlib.contextmanager
    def get_from_data(cls, data):
        with cls._get_from('data', data) as p: yield p
