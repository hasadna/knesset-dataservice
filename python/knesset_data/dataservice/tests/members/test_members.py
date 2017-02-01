import unittest
from knesset_data.dataservice.members import Member


class TestMembers(unittest.TestCase):

    def test_member(self):
        member_id = 1
        member = Member.get(member_id)
        members = Member.get_page(order_by=('id', 'asc'))
        self.assertEqual(member.name, members.next().name)

    def test_members(self):
        members = Member.get_all()
        self.assertTrue(len([True for member in members]) > 700)
