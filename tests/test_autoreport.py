# coding: utf-8

from __future__ import (unicode_literals, print_function,
                        absolute_import, division)

import unittest
import pytest

from formpack import FormPack
from .fixtures import build_fixture


class TestAutoReport(unittest.TestCase):

    maxDiff = None

    def test_list_fields_on_packs(self):

        title, schemas, submissions = build_fixture('restaurant_profile')
        fp = FormPack(schemas, title)

        fields = fp.get_fields_for_versions()

        field_names = [field.name for field in fields]
        assert field_names == ['restaurant_name', 'location', 'eatery_type']

        field_types = [field.__class__.__name__ for field in fields]
        assert field_types == ['TextField', 'FormGPSField',
                               'FormChoiceFieldWithMultipleSelect']

    def test_list_fields_from_many_versions_on_packs(self):

        title, schemas, submissions = build_fixture('site_inspection')
        fp = FormPack(schemas, title)
        self.assertEqual(len(fp.versions), 5)

        fields = {
            field.name: field for field in fp.get_fields_for_versions(
                fp.versions.keys())
        }
        field_names = sorted(fields.keys())
        self.assertListEqual(field_names, [
            'did_you_find_the_site',
            'inspector',
            'is_plant_life_encroaching',
            'is_the_gate_secure',
            'ping',
            'please_rate_the_impact_of_any_defects_observed',
            'rssi',
            'was_there_damage_to_the_site',
            'was_there_damage_to_the_site_dupe',
        ])
        field_types = [fields[name].__class__.__name__ for name in field_names]
        self.assertListEqual(field_types, [
            'FormChoiceField',
            'TextField',
            'FormChoiceField',
            'FormChoiceField',
            'NumField',
            'FormChoiceField',
            'NumField',
            'FormChoiceField',
            'FormChoiceField',
        ])

    def test_simple_report(self):

        title, schemas, submissions = build_fixture('restaurant_profile')
        fp = FormPack(schemas, title)

        report = fp.autoreport()
        stats = report.get_stats(submissions, lang='french')

        assert stats.submissions_count == 4

        stats = [(repr(f), n, d) for f, n, d in stats]

        assert list(stats) == [
            (
             "<TextField name='restaurant_name' type='text'>",
             'nom du restaurant',
                  {'frequency': [('Taco Truck', 1),
                                    ('Harvest', 1),
                                    ('Los pollos hermanos', 1),
                                    ('Wololo', 1)],
                  'not_provided': 0,
                  'percentage': [('Taco Truck', 25.00),
                                    ('Harvest', 25.00),
                                    ('Los pollos hermanos', 25.00),
                                    ('Wololo', 25.00)],
                  'provided': 4,
                  'show_graph': False,
                  'total_count': 4}),
            (
             "<FormGPSField name='location' type='geopoint'>",
             'lieu',
                  {'not_provided': 0,
                  'provided': 4,
                  'show_graph': False,
                  'total_count': 4}),
            (
             "<FormChoiceFieldWithMultipleSelect name='eatery_type' type='select_multiple'>",
             'type de restaurant',
                  {'frequency': [('traditionnel', 2), ('avec vente \xe0 emporter', 1)],
                  'not_provided': 1,
                  'percentage': [('traditionnel', 50.00),
                                    ('avec vente \xe0 emporter', 25.00)],
                  'provided': 3,
                  'show_graph': True,
                  'total_count': 4})
         ]

    def test_rich_report(self):

        title, schemas, submissions = build_fixture('auto_report')
        fp = FormPack(schemas, title)

        report = fp.autoreport()
        stats = report.get_stats(submissions)

        assert stats.submissions_count == 6

        stats = [(unicode(repr(f)), n, d) for f, n, d in stats]

        assert list(stats) == [
            (
             "<TextField name='restaurant_name' type='text'>",
             'restaurant_name',
                  {'frequency': [('Felipes', 2),
                                 ('The other one', 2),
                                   ('That one', 1)],
                   'not_provided': 1,
                   'percentage': [('Felipes', 33.33),
                                   ('The other one', 33.33),
                                   ('That one', 16.67)],
                   'provided': 5,
                   'show_graph': False,
                   'total_count': 6}
            ),
            (
             "<FormGPSField name='location' type='geopoint'>",
             'location',
                  {'not_provided': 1,
                   'provided': 5,
                   'show_graph': False,
                   'total_count': 6}
            ),
            (
             "<DateField name='when' type='date'>",
             'when',
                  {'frequency': [('2001-01-01', 2),
                                  ('2002-01-01', 2),
                                  ('2003-01-01', 1)],
                   'not_provided': 1,
                   'percentage': [('2001-01-01', 33.33),
                                    ('2002-01-01', 33.33),
                                    ('2003-01-01', 16.67)],

                   'provided': 5,
                   'show_graph': True,
                   'total_count': 6}
            ),
            (
             "<NumField name='howmany' type='integer'>",
             'howmany',
                  {'mean': 1.6,
                   'median': 2,
                   'mode': 2,
                   'not_provided': 1,
                   'provided': 5,
                   'show_graph': False,
                   'stdev': 0.5477225575051661,
                   'total_count': 6}
            )
        ]

    def test_simple_multi_version_report(self):
        title, schemas, submissions = build_fixture('site_inspection')
        fp = FormPack(schemas, title)

        report = fp.autoreport(versions=fp.versions.keys())
        stats = report.get_stats(submissions)

        self.assertEqual(stats.submissions_count, 10)

        stats = [(repr(f), n, d) for f, n, d in stats]

        self.assertListEqual(stats, [
            (
               "<TextField name='inspector' type='text'>",
                u'inspector',
                   {u'frequency': [(u'burger', 5), (u'clouseau', 5)],
                    u'not_provided': 0,
                    u'percentage': [(u'burger', 50.0), (u'clouseau', 50.0)],
                    u'provided': 10,
                    u'show_graph': False,
                    u'total_count': 10}
            ),
            (
               "<FormChoiceField name='did_you_find_the_site' type='select_one'>",
                u'did_you_find_the_site',
                   {u'frequency': [(0, 4), (1, 4), (u'yes', 1), (u'no', 1)],
                    u'not_provided': 0,
                    u'percentage': [(0, 40.0),
                                    (1, 40.0),
                                    (u'yes', 10.0),
                                    (u'no', 10.0)],
                    u'provided': 10,
                    u'show_graph': True,
                    u'total_count': 10}
            ),
            (
               "<FormChoiceField name='was_there_damage_to_the_site' type='select_one'>",
                u'was_there_damage_to_the_site',
                   {u'frequency': [(0, 2), (1, 2), (u'yes', 1)],
                    u'not_provided': 5,
                    u'percentage': [(0, 40.0), (1, 40.0), (u'yes', 20.0)],
                    u'provided': 5,
                    u'show_graph': True,
                    u'total_count': 10}
            ),
            (
               "<FormChoiceField name='was_there_damage_to_the_site_dupe' type='select_one'>",
                u'was_there_damage_to_the_site_dupe',
                   {u'frequency': [(1, 1), (u'yes', 1)],
                    u'not_provided': 8,
                    u'percentage': [(1, 50.0), (u'yes', 50.0)],
                    u'provided': 2,
                    u'show_graph': True,
                    u'total_count': 10}
            ),
            (
               "<NumField name='ping' type='integer'>",
                u'ping',
                   {u'mean': 238.4,
                    u'median': 123,
                    u'mode': u'*',
                    u'not_provided': 5,
                    u'provided': 5,
                    u'show_graph': False,
                    u'stdev': 255.77392361224003,
                    u'total_count': 10}
            ),
            (
               "<NumField name='rssi' type='integer'>",
                u'rssi',
                   {u'mean': 63.8,
                    u'median': u'65',
                    u'mode': u'*',
                    u'not_provided': 5,
                    u'provided': 5,
                    u'show_graph': False,
                    u'stdev': 35.22357165308481,
                    u'total_count': 10}
            ),
            (
               "<FormChoiceField name='is_the_gate_secure' type='select_one'>",
                u'is_the_gate_secure',
                   {u'frequency': [(0, 2), (1, 2), (u'no', 1)],
                    u'not_provided': 5,
                    u'percentage': [(0, 40.0), (1, 40.0), (u'no', 20.0)],
                    u'provided': 5,
                    u'show_graph': True,
                    u'total_count': 10}
            ),
            (
               "<FormChoiceField name='is_plant_life_encroaching' type='select_one'>",
                u'is_plant_life_encroaching',
                   {u'frequency': [(0, 1), (1, 3), (u'yes', 1)],
                    u'not_provided': 5,
                    u'percentage': [(0, 20.0), (1, 60.0), (u'yes', 20.0)],
                    u'provided': 5,
                    u'show_graph': True,
                    u'total_count': 10}
            ),
            (
               "<FormChoiceField name='please_rate_the_impact_of_any_defects_observed' type='select_one'>",
                u'please_rate_the_impact_of_any_defects_observed',
                   {u'frequency': [(u'moderate', 4), (u'severe', 3), (u'low', 3)],
                    u'not_provided': 0,
                    u'percentage': [(u'moderate', 40.0),
                                    (u'severe', 30.0),
                                    (u'low', 30.0)],
                    u'provided': 10,
                    u'show_graph': True,
                    u'total_count': 10}
            )
        ])

'''
    def test_disaggregate(self):

            title, schemas, submissions = build_fixture('auto_report')
            fp = FormPack(schemas, title)

            report = fp.autoreport()
            stats = report.get_stats(submissions, split_by="when")

            assert stats.submissions_count == 6

            stats = [(unicode(repr(f)), n, d) for f, n, d in stats]

            assert list(stats) == [("<TextField name='restaurant_name' type='text'>",
                    'restaurant_name',
                    {'not_provided': 1,
                     'provided': 5,
                     'show_graph': False,
                     'total_count': 6,
                     'values': [('Felipes',
                                  {'frequency': [('2001-01-01', 2),
                                                  ('2002-01-01', 0),
                                                  ('2003-01-01', 0)],
                                   'percentage': [('2001-01-01', 33.33),
                                                   ('2002-01-01', 0.00),
                                                   ('2003-01-01', 0.00)]}),
                                 ('The other one',
                                  {'frequency': [('2001-01-01', 0),
                                                  ('2002-01-01', 2),
                                                  ('2003-01-01', 0)],
                                   'percentage': [('2001-01-01', 0.00),
                                                   ('2002-01-01', 33.33),
                                                   ('2003-01-01', 0.00)]}),
                                 ('That one',
                                  {'frequency': [('2001-01-01', 0),
                                                  ('2002-01-01', 0),
                                                  ('2003-01-01', 1)],
                                   'percentage': [('2001-01-01', 0.00),
                                                   ('2002-01-01', 0.00),
                                                   ('2003-01-01', 16.67)]})]}),
                   ("<FormGPSField name='location' type='geopoint'>",
                    'location',
                    {'not_provided': 1,
                     'provided': 5,
                     'show_graph': False,
                     'total_count': 6}),
                   ("<NumField name='howmany' type='integer'>",
                    'howmany',
                    {'not_provided': 1,
                     'provided': 5,
                     'show_graph': False,
                     'total_count': 6,
                     'values': (('2001-01-01',
                                  {'mean': 1.5,
                                   'median': 1.5,
                                   'mode': '*',
                                   'stdev': 0.7071067811865476}),
                                 ('2002-01-01',
                                  {'mean': 2.0, 'median': 2.0, 'mode': 2, 'stdev': 0.0}),
                                 ('2003-01-01',
                                  {'mean': 1.0,
                                   'median': 1,
                                   'mode': '*',
                                   'stdev': u'*'}))})]
'''
