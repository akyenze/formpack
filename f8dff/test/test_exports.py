# coding: utf-8

from __future__ import (unicode_literals, print_function,
                        absolute_import, division)

import unittest
import json

from f8dff.models.formpack.pack import FormPack
from f8dff.fixtures import build_fixture


customer_satisfaction = build_fixture('customer_satisfaction')
restaurant_profile = build_fixture('restaurant_profile')


class TestFormPackExport(unittest.TestCase):
    maxDiff = None

    def test_generator_export(self):
        forms = FormPack(**customer_satisfaction)
        values_exported = forms._export_to_lists()
        expected = [["submissions", [
                        ["restaurant_name", "customer_enjoyment"],
                        [
                            ["Felipes", "yes"],
                            ["Dunkin Donuts", "no"],
                            ["McDonalds", "no"]]]
                     ]]

        self.assertEqual(expected, values_exported)

    def test_generator_export_translation_headers(self):
        fp = FormPack(**restaurant_profile)
        self.assertEqual(len(fp.versions), 2)
        self.assertEqual(len(fp[1].translations), 2)

        # by default, exports use the question 'name' attribute
        headers = fp._export_to_lists()[0][1][0]
        self.assertEquals(headers, ['restaurant_name', 'location'])

        # the first translation in the list is the translation that
        # appears first in the column list. in this case, 'label::english'
        translations = fp[1].translations
        headers = fp._export_to_lists(header_lang=translations[0])[0][1][0]
        self.assertEquals(headers, ['Restaurant name', 'Location'])

        formpack = FormPack(**restaurant_profile)
        headers = formpack._export_to_lists(header_lang=translations[1])
        self.assertEquals(headers[0][1][0], ['nom du restaurant', 'Location'])

        # "default" use the "Label" field
        formpack = FormPack(**restaurant_profile)
        headers = formpack._export_to_lists(header_lang="default",
                                            form_version='rpv1')
        self.assertEquals(headers[0][1][0], ['restaurant name', 'location'])
