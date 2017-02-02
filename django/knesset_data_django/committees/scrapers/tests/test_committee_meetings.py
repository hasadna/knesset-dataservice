# -*- coding: utf-8 -*-
from django.test import TestCase
from ...models import CommitteeMeeting, Committee
from ..committee_meetings import CommitteeMeetingsScraper
from datetime import datetime, date
from ....common.testing.mocks import MockDataserviceObject
from knesset_data.dataservice.committees import CommitteeMeeting as DataserviceCommitteeMeeting


class MockCOmmitteeMeetingsScraper(CommitteeMeetingsScraper):
    """override functions that gets data from external services"""

    def __init__(self, mock_meetings_data, **kwargs):
        super(MockCOmmitteeMeetingsScraper, self).__init__(**kwargs)
        self._mock_meetings_data = mock_meetings_data

    def _get_meetings(self, committee_id, from_date, to_date):
        return [MockDataserviceObject(DataserviceCommitteeMeeting, **meeting)
                for meeting in self._mock_meetings_data
                if meeting["committee_id"] == committee_id]

    def _reparse_protocol(self, meeting):
        pass  # protocol parsing should be tested in it's own test case


class CommitteeMeetingsScraperTestCase(TestCase):
    longMessage = True  # works better when using custom assertion messages

    def assertComitteeMeetings(self, from_date, to_date, committees, model_meetings, dataservice_meetings,
                               expected_scrape_return_values, expected_model_meetings):
        CommitteeMeeting.objects.all().delete()
        Committee.objects.all().delete()
        self.assertEqual(CommitteeMeeting.objects.all().count(), 0)
        self.assertEqual(Committee.objects.all().count(), 0)
        [Committee.objects.create(**committee) for committee in committees]
        self.assertEqual(Committee.objects.all().count(), len(committees))
        [CommitteeMeeting.objects.create(**meeting) for meeting in model_meetings]
        self.assertEqual(CommitteeMeeting.objects.all().count(), len(model_meetings))
        committee_ids = [committee["id"] for committee in committees]
        return_values_iterator = iter(expected_scrape_return_values)
        for committee, meetings in MockCOmmitteeMeetingsScraper(dataservice_meetings).scrape(from_date, to_date, committee_ids):
            for dataservice_meeting, model_meeting, error in meetings:
                assertion_msg = "committee.id={}, dataservice_meeting.id={}".format(committee.id, dataservice_meeting.id)
                expected_values = return_values_iterator.next()
                self.assertEqual(committee.id, expected_values["committee_id"], assertion_msg)
                self.assertEqual(error, expected_values["error"], assertion_msg)
                if expected_values['has_model_meeting']:
                    self.assertIsInstance(model_meeting, CommitteeMeeting, assertion_msg)
                else:
                    self.assertIsNone(model_meeting, assertion_msg)
                self.assertEqual(dataservice_meeting.id, expected_values['dataservice_meeting_id'], assertion_msg)
        self.assertEqual(CommitteeMeeting.objects.all().count(), len(expected_model_meetings))
        for expected_meeting in expected_model_meetings:
            actual_meeting = CommitteeMeeting.objects.get(knesset_id=expected_meeting["knesset_id"])
            for attr_name in expected_meeting:
                assertion_msg = 'expected_meeting["knesset_id"]={}, attr_name={}'.format(expected_meeting["knesset_id"], attr_name)
                self.assertEqual(getattr(actual_meeting, attr_name), expected_meeting[attr_name], assertion_msg)

    def test(self):
        self.assertComitteeMeetings(from_date=datetime(2015, 6, 20),
                                    to_date=datetime(2015, 6, 23),

                                    # existing committees in Open Knesset DB
                                    committees=[{"id": 1, "knesset_id": 1},
                                                {"id": 2, "knesset_id": 2},
                                                {"id": 3, "knesset_id": 3}],

                                    # existing committee meetings - to check for update scenario
                                    model_meetings=[{"committee_id": 2,
                                                     "date_string": u"21/06/2015",
                                                     "date": datetime(2015, 6, 21, 5, 4, 3),
                                                     "topics": u"ישיבת ועדה 1",
                                                     "datetime": datetime(2015, 6, 21, 5, 4, 3),
                                                     "knesset_id": 3,
                                                     "src_url": "http://fake-url-committee-meeting-1/",},
                                                    {"committee_id": 2,
                                                     "date_string": u"22/06/2015",
                                                     "date": datetime(2015, 6, 22, 5, 4, 3),
                                                     "topics": u"ישיבת ועדה 2",
                                                     "datetime": datetime(2015, 6, 22, 5, 4, 3),
                                                     "knesset_id": 4,
                                                     "src_url": "http://fake-url-committee-meeting-2/",}],

                                    # mock dataservice meetings to return
                                    dataservice_meetings=[{"id": 1,
                                                           "committee_id": 1,
                                                           "datetime": datetime(2015, 6, 21, 5, 4, 3),
                                                           "title": u"ישיבת ועדה 1",
                                                           "url": "http://fake-url-committee-meeting-1/",
                                                           "session_content": None},
                                                          {"id": 2,
                                                           "committee_id": 1,
                                                           "datetime": datetime(2015, 6, 22, 5, 4, 3),
                                                           "title": None,
                                                           "url": "http://fake-url-committee-meeting-2/",
                                                           "session_content": u"ישיבת ועדה 2"},
                                                          {"id": 3,
                                                           "committee_id": 2,
                                                           "datetime": datetime(2015, 6, 21, 5, 4, 3),
                                                           "title": u"ישיבת ועדה 1",
                                                           "url": "http://fake-url-committee-meeting-1/",
                                                           "session_content": None},
                                                          {"id": 4,
                                                           "committee_id": 2,
                                                           "datetime": datetime(2015, 6, 22, 5, 4, 3),
                                                           "title": None,
                                                           "url": "http://fake-url-committee-meeting-2/",
                                                           "session_content": u"ישיבת ועדה 2"},
                                                          {"id": 5,
                                                           "committee_id": 3,
                                                           "datetime": datetime(2015, 6, 22, 5, 4, 3),
                                                           "title": None,
                                                           "url": "",
                                                           "session_content": u"ישיבת ועדה ללא URL"}],

                                    # expected return values from the scraper generator
                                    expected_scrape_return_values=[{"committee_id": 1,
                                                                    "error": "",
                                                                    "has_model_meeting": True,
                                                                    "dataservice_meeting_id": 1},
                                                                   {"committee_id": 1,
                                                                    "error": "",
                                                                    "has_model_meeting": True,
                                                                    "dataservice_meeting_id": 2},
                                                                   {"committee_id": 2,
                                                                    "error": "meeting exists in DB",
                                                                    "has_model_meeting": False,
                                                                    "dataservice_meeting_id": 3},
                                                                   {"committee_id": 2,
                                                                    "error": "meeting exists in DB",
                                                                    "has_model_meeting": False,
                                                                    "dataservice_meeting_id": 4},
                                                                   {"committee_id": 3,
                                                                    "error" : "missing meeting url",
                                                                    "has_model_meeting": False,
                                                                    "dataservice_meeting_id": 5}],

                                    # expected model meetings object after scraping
                                    expected_model_meetings=[{"committee_id": 1,
                                                              "date_string": u"21/06/2015",
                                                              "date": date(2015, 6, 21),
                                                              "topics": u"ישיבת ועדה 1",
                                                              "datetime": datetime(2015, 6, 21, 5, 4, 3),
                                                              "knesset_id": 1,
                                                              "src_url": "http://fake-url-committee-meeting-1/",},
                                                             {"committee_id": 1,
                                                              "date_string": u"22/06/2015",
                                                              "date": date(2015, 6, 22),
                                                              "topics": u"ישיבת ועדה 2",
                                                              "datetime": datetime(2015, 6, 22, 5, 4, 3),
                                                              "knesset_id": 2,
                                                              "src_url": "http://fake-url-committee-meeting-2/",},
                                                             {"committee_id": 2,
                                                              "date_string": u"21/06/2015",
                                                              "date": date(2015, 6, 21),
                                                              "topics": u"ישיבת ועדה 1",
                                                              "datetime": datetime(2015, 6, 21, 5, 4, 3),
                                                              "knesset_id": 3,
                                                              "src_url": "http://fake-url-committee-meeting-1/",},
                                                             {"committee_id": 2,
                                                              "date_string": u"22/06/2015",
                                                              "date": date(2015, 6, 22),
                                                              "topics": u"ישיבת ועדה 2",
                                                              "datetime": datetime(2015, 6, 22, 5, 4, 3),
                                                              "knesset_id": 4,
                                                              "src_url": "http://fake-url-committee-meeting-2/",}, ])
