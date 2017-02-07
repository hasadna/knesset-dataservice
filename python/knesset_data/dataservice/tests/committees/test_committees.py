import unittest


from knesset_data.dataservice.committees import Committee


class TestCommittees(unittest.TestCase):

    def test_committee(self):
        committee_id = 1
        committee = Committee.get(committee_id)
        committees = Committee.get_page(order_by=('id', 'asc'))
        self.assertEqual(committee.name, committees.next().name)

    def test_active_committees(self):
        committees = Committee.get_all_active_committees()
        first_committee = committees.next()
        committee = Committee.get(first_committee.id)
        self.assertEqual(committee.name, first_committee.name)
        self.assertTrue(committee.portal_link!=None and committee.portal_link != '' and committee.end_date==None)
