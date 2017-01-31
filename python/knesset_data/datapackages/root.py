from knesset_data.datapackages.base import BaseDatapackage, DatapackageResource
from knesset_data.dataservice.datapackages import DataserviceDatapackage


class RootDatapackage(BaseDatapackage):

    def __init__(self, base_path):
        super(RootDatapackage, self).__init__(descriptor={
            "name": "knesset-data"
        }, default_base_path=base_path)

    def _load_resources(self, descriptor, base_path):
        descriptor["resources"] = [
            DatapackageResource("dataservice", base_path, DataserviceDatapackage)
        ]
        return super(RootDatapackage, self)._load_resources(descriptor, base_path)
