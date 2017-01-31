import datetime

import requests
from bs4 import BeautifulSoup, Tag
from requests import Request
import logging

from knesset_data.dataservice.constants import SERVICE_URLS
import knesset_data.dataservice.utils as ds_utils
from knesset_data.utils.github import github_add_or_update_issue
from knesset_data.dataservice.exceptions import KnessetDataServiceRequestException
from copy import deepcopy
from collections import OrderedDict


logger=logging.getLogger(__name__)


class BaseKnessetDataServiceField(object):
    DEPENDS_ON_OBJ_FIELDS = False

    def __init__(self, json_table_schema="string"):
        self._json_table_schema = json_table_schema

    def get_value(self, entry):
        raise Exception('must be implemented by extending classes')

    def get_order_by_field(self):
        raise Exception(
            'must be implemented by extending classes if order by support is needed for this field')

    def set_value(self, obj, attr_name, entry):
        setattr(obj, attr_name, self.get_value(entry))

    def get_json_table_schema_field(self, name=None):
        if isinstance(self._json_table_schema, dict):
            schema = deepcopy(self._json_table_schema)
        else:
            schema = {"type": self._json_table_schema}
        if name:
            schema["name"] = name
        return schema


class KnessetDataServiceSimpleField(BaseKnessetDataServiceField):
    def __init__(self, knesset_field_name, json_table_schema=None):
        super(KnessetDataServiceSimpleField, self).__init__(json_table_schema)
        self._knesset_field_name = knesset_field_name

    def get_value(self, entry):
        data = entry['data']
        return data[self._knesset_field_name.lower()]

    def get_order_by_field(self):
        return self._knesset_field_name


class KnessetDataServiceStrptimeField(KnessetDataServiceSimpleField):
    def __init__(self, knesset_field_name, strptime_format='%H:%M'):
        super(KnessetDataServiceStrptimeField, self).__init__(knesset_field_name)
        self._strptime_format = strptime_format

    def get_value(self, entry, obj=None):
        str = super(KnessetDataServiceStrptimeField, self).get_value(entry)
        return datetime.datetime.strptime(str, self._strptime_format)


class KnessetDataServiceDateTimeField(BaseKnessetDataServiceField):
    DEPENDS_ON_OBJ_FIELDS = True

    def __init__(self, date_attr_name, time_attr_name):
        super(KnessetDataServiceDateTimeField, self).__init__()
        self._date_attr_name = date_attr_name
        self._time_attr_name = time_attr_name

    def set_value(self, obj, attr_name, entry):
        value = datetime.datetime.combine(getattr(obj, self._date_attr_name).date(),
                                          getattr(obj, self._time_attr_name).time())
        setattr(obj, attr_name, value)


class KnessetDataServiceLambdaField(BaseKnessetDataServiceField):
    DEPENDS_ON_OBJ_FIELDS = True

    def __init__(self, func):
        super(KnessetDataServiceLambdaField, self).__init__()
        self._func = func

    def set_value(self, obj, attr_name, entry):
        setattr(obj, attr_name, self._func(obj, entry))


class BaseKnessetDataServiceObject(object):
    SERVICE_NAME = None
    METHOD_NAME = None

    # if you need to fetch something that takes longer then 15 seconds to get
    # you should try to split it into multiple small requests (using filters)
    # you can also override on the
    DEFAULT_REQUEST_TIMEOUT_SECONDS = 15

    @classmethod
    def _get_service_name(cls):
        return cls.SERVICE_NAME

    @classmethod
    def _get_method_name(cls):
        return cls.METHOD_NAME

    @classmethod
    def _get_url_base(cls):
        return SERVICE_URLS[cls._get_service_name()] + '/' + cls._get_method_name()

    @classmethod
    def _get_request_exception(cls, original_exception):
        return KnessetDataServiceRequestException(cls._get_service_name(), cls._get_method_name(), original_exception)

    @classmethod
    def _get_soup(cls, url, params=None, proxies=None):
        params = {} if params == None else params
        timeout = params.pop('__timeout__', cls.DEFAULT_REQUEST_TIMEOUT_SECONDS)
        try:
            proxies = proxies if proxies else {}
            response = requests.get(url, params=params, timeout=timeout, proxies=proxies)
        except requests.RequestException, e:
            raise cls._get_request_exception(e)
        if response.status_code != 200:
            raise Exception("invalid response status code: {}".format(response.status_code))
        else:
            return BeautifulSoup(response.content, 'html.parser')

    @classmethod
    def _handle_prop(cls, prop_type, prop_null, prop):
        if prop_null:
            return None
        elif prop_type == '':
            return prop.string
        elif prop_type in ('Edm.Int32', 'Edm.Int16', 'Edm.Byte', 'Edm.Int64'):
            return int(prop.string)
        elif prop_type == 'Edm.Decimal':
            return float(prop.string)
        elif prop_type == 'Edm.DateTime':
            return datetime.datetime.strptime(prop.string.split('.')[0], "%Y-%m-%dT%H:%M:%S")
        elif prop_type == 'Edm.Boolean':
            return prop.string == 'true'
        else:
            raise Exception('unknown prop type: %s' % prop_type)

    @classmethod
    def get_fields(cls):
        if not hasattr(cls, '_fields'):
            if hasattr(cls, "ORDERED_FIELDS"):
                cls._fields = OrderedDict(cls.ORDERED_FIELDS)
            else:
                cls._fields = OrderedDict(((attr_name, getattr(cls, attr_name))
                                           for attr_name in dir(cls)
                                           if isinstance(getattr(cls, attr_name, None), BaseKnessetDataServiceField)))
        return cls._fields

    @classmethod
    def get_json_table_schema(cls):
        return {"fields": [field.get_json_table_schema_field(fieldname)
                           for fieldname, field
                           in cls.get_fields().iteritems()]}


    @classmethod
    def get_field(cls, name=None):
        fields = cls.get_fields()
        return fields[name]

    @classmethod
    def error_report(cls, short_title, msg, content=None):
        title = 'error in %s/%s: %s' % (
            cls._get_service_name(), cls._get_method_name(), short_title)
        if content is not None:
            content = {"content.txt": {"content": content}}
        github_add_or_update_issue(title, msg, content)

    def _set_field_value(self, field, attr_name, entry):
        field.set_value(self, attr_name, entry)

    def all_field_values(self):
        return OrderedDict(((k, getattr(self, k))
                            for k, v
                            in self.get_fields().iteritems()))

    def __init__(self, entry, proxies=None):
        self._session = requests.session()
        self._entry = entry
        self._proxies = proxies if proxies else {}
        for attr_name, field in self.get_fields().iteritems():
            if not field.DEPENDS_ON_OBJ_FIELDS:
                self._set_field_value(field, attr_name, entry)
        for attr_name, field in self.get_fields().iteritems():
            if field.DEPENDS_ON_OBJ_FIELDS:
                self._set_field_value(field, attr_name, entry)


class BaseKnessetDataServiceCollectionObject(BaseKnessetDataServiceObject):
    DEFAULT_ORDER_BY_FIELD = None

    @classmethod
    def _get_url_single(cls, id):
        return u"{url}({id})".format(
            url=cls._get_url_base(),
            id=id
        )

    @classmethod
    def _get_url_page(cls, order_by, results_per_page, page_num):
        url = cls._get_url_base()
        url += '?$top=%s&$skip=%s' % (results_per_page, (page_num - 1) * results_per_page)
        if order_by:
            if isinstance(order_by, (list, tuple)):
                order_by = '%s%%20%s' % order_by
            url += '&$orderby=%s' % order_by
        return url

    @classmethod
    def _parse_entry(cls, entry):
        entry_id = entry.id.string
        entry_links = []
        for link in entry.find_all('link'):
            entry_links.append({'href': link.attrs['href'], 'rel': link.attrs['rel'][0],
                                'title': link.attrs['title']})
        data = {}
        for prop in entry.content.find('m:properties').children:
            if isinstance(prop, Tag):
                prop_tagtype, prop_name = prop.name.split(':')
                prop_type = prop.attrs.get('m:type', '')
                prop_null = (prop.attrs.get('m:null', '') == 'true')
                data[prop_name] = cls._handle_prop(prop_type, prop_null, prop)
        return {
            'id': entry_id,
            'links': entry_links,
            'data': data,
        }

    @classmethod
    def _get_all_pages(cls, start_url, params=None, proxies=None):
        """
        This method is not exposed externally because it might be dangerous
        it will iterate over all the pages, starting at start_url, following next url in each xml
        it's dangerous because there is no stop condition
        so be sure to use it only with some kind of filter in the url to limit number of results
        """
        # Composing URL in advance since the link to the next page already have the params of the
        # first request and using `get_soup` with the params argument creates duplicate params
        next_url = ds_utils.compose_url_get(start_url, params)
        while next_url:
            soup = cls._get_soup(next_url, proxies=proxies)
            for entry in soup.feed.find_all('entry'):
                yield cls(cls._parse_entry(entry))
            next_link = soup.find('link', rel="next")
            next_url = next_link and next_link.attrs.get('href', None)

    @classmethod
    def get(cls, id, proxies=None):
        soup = cls._get_soup(cls._get_url_single(id), proxies=proxies)
        return cls(cls._parse_entry(soup.entry))

    @classmethod
    def get_page(cls, order_by=None, results_per_page=50, page_num=1, proxies=None):
        if not order_by and cls.DEFAULT_ORDER_BY_FIELD:
            order_by = (cls.DEFAULT_ORDER_BY_FIELD, 'desc')
        if order_by:
            order_by_field, order_by_dir = order_by
            order_by_field = cls.get_field(order_by_field).get_order_by_field()
            order_by = order_by_field, order_by_dir
        soup = cls._get_soup(cls._get_url_page(order_by, results_per_page, page_num), proxies=proxies)
        if len(soup.feed.find_all('link', attrs={'rel': 'next'})) > 0:
            raise Exception(
                'looks like you asked for too much results per page, 50 results per page usually works')
        else:
            return (cls(cls._parse_entry(entry)) for entry in soup.feed.find_all('entry'))


class BaseKnessetDataServiceFunctionObject(BaseKnessetDataServiceObject):

    @classmethod
    def _get_url(cls, params):
        return Request('GET', cls._get_url_base(), params=params).prepare().url

    @classmethod
    def _parse_element(cls, element):
        data = {}
        for child in element.children:
            if isinstance(child, Tag):
                name = child.name
                ptype = child.attrs.get('p2:type', '')
                pnull = (child.attrs.get('p2:null', '') == 'true')
                data[name] = cls._handle_prop(ptype, pnull, child)
        return {
            'data': data
        }

    @classmethod
    def get(cls, params, proxies=None):
        soup = cls._get_soup(cls._get_url(params), proxies=proxies)
        return (cls(cls._parse_element(element), proxies=proxies)
                for element
                in soup.find_all('element'))
