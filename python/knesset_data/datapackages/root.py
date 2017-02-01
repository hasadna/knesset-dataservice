from knesset_data.datapackages.base import BaseDatapackage
from knesset_data.dataservice.committees import CommitteesResource, CommitteeMeetingsResource, CommitteeMeetingProtocolsResource
from knesset_data.dataservice.members import MembersResource


class RootDatapackage(BaseDatapackage):

    def __init__(self, base_path):
        super(RootDatapackage, self).__init__(descriptor={
            "name": "knesset-data"
        }, default_base_path=base_path)

    def _load_resources(self, descriptor, base_path):
        descriptor["resources"] = []

        ### dataservice members ###
        members_resource = MembersResource("members", base_path)
        descriptor["resources"] += [members_resource]

        ### dataservice committees ###
        committee_meetings_protocols_resource = CommitteeMeetingProtocolsResource("committee-meetings-protocols",
                                                                                  base_path,
                                                                                  members_resource=members_resource)
        committee_meetings_resource = CommitteeMeetingsResource("committee-meetings",
                                                                base_path,
                                                                protocols_resource=committee_meetings_protocols_resource)
        committees_resource = CommitteesResource("committees",
                                                 base_path,
                                                 meetings_resource=committee_meetings_resource)
        descriptor["resources"] += [committees_resource,
                                    committee_meetings_resource,
                                    committee_meetings_protocols_resource]

        return super(RootDatapackage, self)._load_resources(descriptor, base_path)
