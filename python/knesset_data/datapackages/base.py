from datapackage.datapackage import DataPackage
from datapackage.resource import Resource, TabularResource
import os
import logging
import json
import csv


class BaseResource(Resource):

    def __init__(self, name, parent_datapackage_path, descriptor=None):
        if not descriptor:
            descriptor = {}
        descriptor["name"] = name
        super(BaseResource, self).__init__(descriptor, os.path.join(parent_datapackage_path, name))

    def make(self, parent_name=None, include=None, exclude=None, **kwargs):
        full_name = "-".join([parent_name, self.descriptor["name"]])
        if include and not [True for str in include if len(str) > 0 and full_name.startswith(str)]:
            self.logger.debug("skipping resource '{}' due to include filter".format(full_name))
            return False
        elif exclude and [True for str in exclude if len(str) > 0 and full_name.startswith(str)]:
            self.logger.debug("skipping resource '{}' due to exclude filter".format(full_name))
            return False
        else:
            self.logger.info("making resource '{}'".format(full_name))
            return True

    @property
    def logger(self):
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__module__.replace("knesset_data.", ""))
        return self._logger


class BaseTabularResource(BaseResource, TabularResource):

    def __init__(self, name, parent_datapackage_path, descriptor=None):
        BaseResource.__init__(self, name, parent_datapackage_path, descriptor)


class CsvResource(BaseTabularResource):

    def __init__(self, name, parent_datapackage_path, json_table_schema):
        super(CsvResource, self).__init__(name, parent_datapackage_path)
        self.descriptor.update({
            "path": "{}.csv".format(self._base_path),
            "schema": json_table_schema
        })

    def _get_field_csv_value(self, val, schema):
        if val is None:
            return None
        elif schema["type"] == "datetime":
            return val.isoformat().encode('utf8')
        elif schema["type"] == "integer":
            return val
        elif schema["type"] == "string":
            if hasattr(val, 'encode'):
                return val.encode('utf8')
            else:
                # TODO: check why this happens, I assume it's because of some special field
                return ""
        else:
            # try different methods to encode the value
            for f in (lambda val: val.encode('utf8'),
                      lambda val: unicode(val).encode('utf8')):
                try:
                    return f(val)
                except Exception:
                    pass
            self.logger.warn("failed to encode value for {}".format(schema["name"]))
            return ""

    def _data_generator(self, **make_kwargs):
        raise NotImplementedError('must be implemented in extending classes')

    def make(self, **kwargs):
        if super(CsvResource, self).make(**kwargs):
            csv_path="{}.csv".format(self._base_path)
            self.logger.info('writing csv resource to {}'.format(csv_path))
            fields = self.descriptor["schema"]["fields"]
            with open(csv_path, 'wb') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([field["name"] for field in fields])
                row_num = 0
                for row in self._data_generator(**kwargs):
                    row_num += 1
                    csv_row = []
                    for field in fields:
                        value = self._get_field_csv_value(row[field["name"]], field)
                        csv_row.append(value)
                    csv_writer.writerow(csv_row)
            return True


class DatapackageResource(BaseResource):
    """
    A custom resource which contains a datapackage
    """

    def __init__(self, name, parent_datapackage_path, datapackage_class):
        super(DatapackageResource, self).__init__(name, parent_datapackage_path)
        self.descriptor["path"] = os.path.join(self._base_path, "datapackage.json")
        self._datapackage_class = datapackage_class

    def make(self, **kwargs):
        # remove include / exclude rules - only for datapackage resources, because otherwise it prevents going deeper in the package tree
        exclude = kwargs.pop("exclude", None)
        include = kwargs.pop("include", None)
        if super(DatapackageResource, self).make(**kwargs):
            kwargs["include"] = include
            kwargs["exclude"] = exclude
            if not os.path.exists(self._base_path):
                os.mkdir(self._base_path)
            name = self.descriptor["name"]
            if kwargs.get("parent_name", None):
                name = "{}-{}".format(kwargs.get("parent_name", None), name)
            datapackage = self._datapackage_class(descriptor={"name": name},
                                                  default_base_path=self._base_path)
            datapackage.make(**kwargs)
            return True


class BaseDatapackage(DataPackage):

    def _load_resources(self, descriptor, base_path):
        resources = []
        for i, resource in enumerate(descriptor["resources"]):
            if isinstance(resource, BaseResource):
                json_resource = resource.descriptor
            else:
                json_resource = resource
            descriptor["resources"][i] = json_resource
            resources.append(resource)
        return resources

    @property
    def resources(self):
        return self._resources

    def make(self, **kwargs):
        self.logger.info('making datapackage: "{}", base path: "{}"'.format(self.descriptor["name"], self.base_path))
        if not os.path.exists(self.base_path):
           os.mkdir(self.base_path)
        self.logger.info('making resources')
        for resource in self.resources:
            if isinstance(resource, BaseResource):
                kwargs["parent_name"] = self.descriptor["name"]
                try:
                    if resource.make(**kwargs):
                        resource.descriptor.update({"error": False, "skipped": False})
                    else:
                        resource.descriptor.update({"error": False, "skipped": True})
                except Exception, e:
                    if kwargs.get('force', False):
                        self.logger.error('exception trying to make resource')
                        self.logger.exception(e)
                        resource.descriptor.update({"error": True, "skipped": True})
                    else:
                        raise e
        self.logger.info('writing datapackage.json')
        with open(os.path.join(self.base_path, "datapackage.json"), 'w') as f:
            f.write(json.dumps(self.descriptor, indent=True)+"\n")
        self.logger.info('done')

    @property
    def logger(self):
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__module__.replace("knesset_data.", ""))
        return self._logger
