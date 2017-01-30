from knesset_data.datapackages.base import BaseDatapackage, DatapackageResource
from .committees import CommitteesResource, ActiveCommitteesResource, MainCommitteesResource, CommitteeMeetingsDatapackage


class DataserviceDatapackage(BaseDatapackage):
    name="knesset-data-dataservice"

    def _load_resources(self, descriptor, base_path):
        descriptor["resources"] = [
            # committees
            CommitteesResource("all-committees", base_path),
            ActiveCommitteesResource("active-committees", base_path),
            MainCommitteesResource("main-committees", base_path),

            # committee meetings
            DatapackageResource("committee-meetings", base_path, CommitteeMeetingsDatapackage)
        ]
        return super(DataserviceDatapackage, self)._load_resources(descriptor, base_path)
