# -*- coding: utf-8 -*-
from unittest import TestCase
from knesset_data.dataservice.laws import PrivateLaw, PrivateLawMk
from datetime import datetime


class TestLaws(TestCase):

    def test_law(self):
        law = PrivateLaw.get(318)
        self.assertEqual(law.id, 318)
        self.assertEqual(law.number, 1044)
        # see bug #68 about the excessive spaces
        self.assertEqual(law.name, ' '+u'רכב עולים - ביטול פטור ממיסים עקיפים'+(' '*153)+u'התש”ס-1999')
        self.assertEqual(law.subject, u'ביטול פטור ממיסים עקיפים'+(' '*276))
        self.assertEqual(law.suggest_date, datetime(1999, 12, 13))
        self.assertEqual(law.creation_date, datetime(2001, 5, 2, 9, 36, 50))
        self.assertEqual(law.type_id, 1)
        self.assertEqual(law.link, '1044.rtf')
        self.assertEqual(law.knesset_id, 15)
        # due to bug #69 we don't know for sure if this url will be correct or not, it's an educated guess
        self.assertEqual(law.guess_link_url(), 'http://knesset.gov.il/privatelaw/data/15/1044.rtf')
        self.assertEqual(PrivateLawMk.get_by_plaw_id(318).next().mk_id, 119)

    def test_law_mks(self):
        law_mks = list(PrivateLawMk.get_by_plaw_id(321))
        self.assertEqual(len(law_mks), 4)
        law_mks = {
            law_mk.mk_id: {
                'id': law_mk.id,
                'mk_id': law_mk.mk_id,
                'law_number': law_mk.law_number,
                'mk_suggest': law_mk.mk_suggest,
                'plaw_id': law_mk.plaw_id
            }
            for law_mk in law_mks
        }
        self.assertDictEqual(law_mks[212], {'id': 283, 'mk_id':212, 'law_number':945, 'mk_suggest': 0, 'plaw_id':321})
        self.assertDictEqual(law_mks[105], {'id': 284, 'mk_id':105, 'law_number':945, 'mk_suggest': 1, 'plaw_id':321})
        self.assertDictEqual(law_mks[1], {'id': 464, 'mk_id':1, 'law_number':945, 'mk_suggest': 1, 'plaw_id':321})
        self.assertDictEqual(law_mks[13], {'id': 468, 'mk_id':13, 'law_number':945, 'mk_suggest': 1, 'plaw_id':321})
