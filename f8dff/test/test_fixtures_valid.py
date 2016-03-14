# coding: utf-8

from __future__ import (unicode_literals, print_function,
                        absolute_import, division)

import unittest

from ..models.formpack.pack import FormPack
from ..fixtures import build_fixture


sanitation_report = build_fixture('sanitation_report')
customer_satisfaction = build_fixture('customer_satisfaction')
restaurant_profile = build_fixture('restaurant_profile')
favcolor = build_fixture('favcolor')


class TestFormPackFixtures(unittest.TestCase):
    maxDiff = None

    def _reimport(self, fd):
        fd2 = FormPack(**fd.to_dict())
        return fd2

    def test_sanitation_report(self):
        '''
        sanitation_report
        '''
        fd = FormPack(**sanitation_report)
        self.assertEqual(len(fd.versions), 1)
        self.assertEqual(fd._submissions_count(), 4)
        v0 = fd[0]
        self.assertEqual(list(v0.fields.keys()),
                         [u'restaurant_name',
                          u'restaurant_rating',
                          u'report_date'])

    def test_grouped_questions(self):
        '''
        questions groups
        '''
        fd = FormPack(**build_fixture('grouped_questions'))
        self.assertEqual(len(fd.versions), 1)
        self.assertEqual(fd._submissions_count(), 2)
        self.assertEqual(list(fd[0].fields.keys()),
                         ['q1', 'g1q1', 'g2q1', 'qz'])

    def test_customer_satisfaction(self):
        '''
        customer_satisfaction
        '''
        fxt = customer_satisfaction
        fd = FormPack(**customer_satisfaction)
        v0 = fd[0]
        self.assertEqual(len(fd.versions), 1)
        self.assertEqual(fd._submissions_count(), 3)
        self.assertEqual(list(v0.fields.keys()),
                         [u'restaurant_name', u'customer_enjoyment'])
        self.assertEqual(sorted(fd.to_dict().keys()),
                         sorted(fxt.keys()))
        self.assertEqual(fd.to_dict(), fxt)
        self.assertEqual(fd.to_dict(), customer_satisfaction)

    def test_restaurant_profile(self):
        fxt = restaurant_profile
        fd = FormPack(**fxt)
        self.assertEqual(len(fd.versions), 3)
        v0 = fd[0]
        self.assertEqual(list(v0.fields.keys()),
                         [u'restaurant_name', u'location'])

        self.assertEqual(sorted(fd.to_dict().keys()),
                         sorted(fxt.keys()))

        self.assertEqual(fd.to_dict(), fxt)

        v0.submit([u'Dominos', u'-12.22 12.22'])
        v0.submit(restaurant_name=u'Boston Market', location=u'-13.22 13.22')
        v0.submit({u'restaurant_name': u'Starbx', u'location': u'-11.2 11.2'})
        self.assertEqual(fd.to_dict(), self._reimport(fd).to_dict())

    def test_xml_instances_loaded(self):
        '''
        favcolor has submissions_xml specified
        '''
        fd = FormPack(**favcolor)
        self.assertEqual(len(fd.versions), 2)
        self.assertGreater(fd._submissions_count(), 0,
                           'submission count should be > 0')
