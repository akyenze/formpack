# coding: utf-8

# This module might be more appropriately named "standardize_content"
# and pass content through to formpack.utils.replace_aliases during
# the standardization step: expand_content_in_place(...)

from __future__ import (unicode_literals, print_function,
                        absolute_import, division)

from copy import deepcopy
from collections import OrderedDict
import re

from .array_to_xpath import EXPANDABLE_FIELD_TYPES
from .replace_aliases import META_TYPES
from ..constants import UNTRANSLATED, OR_OTHER_COLUMN

REMOVE_EMPTY_STRINGS = True
# this will be used to check which version of formpack was used to compile the
# asset content
SCHEMA_VERSION = "1"


def _expand_translatable_content(content, row, col_shortname,
                                 special_column_details):
    _scd = special_column_details
    if 'translation' in _scd:
        translations = content['translations']
        cur_translation = _scd['translation']
        cur_translation_index = translations.index(cur_translation)
        _expandable_col = _scd['column']
        if _expandable_col not in row:
            row[_expandable_col] = [None] * len(translations)
        elif not isinstance(row[_expandable_col], list):
            _oldval = row[_expandable_col]
            _nti = translations.index(UNTRANSLATED)
            row[_expandable_col] = [None] * len(translations)
            row[_expandable_col][_nti] = _oldval
        if col_shortname != _expandable_col:
            row[_expandable_col][cur_translation_index] = row[col_shortname]
            del row[col_shortname]


def _get_translations_from_special_cols(special_cols, translations):
    translated_cols = []
    for (colname, parsedvals) in special_cols.iteritems():
        if 'translation' in parsedvals:
            translated_cols.append(parsedvals['column'])
            if parsedvals['translation'] not in translations:
                translations.append(parsedvals['translation'])
    return (translations, set(translated_cols))


def expand_content_in_place(content):
    (specials, translations, transl_cols) = _get_special_survey_cols(content)

    if len(translations) > 0:
        content['translations'] = translations
        content['translated'] = transl_cols

    survey_content = content.get('survey', [])
    _metas = []

    for row in survey_content:
        if 'name' in row and row['name'] == None:
            del row['name']
        if 'type' in row:
            _type = row['type']
            if _type in META_TYPES:
                _metas.append(row)
            if isinstance(_type, basestring):
                row.update(_expand_type_to_dict(row['type']))
            elif isinstance(_type, dict):
                # legacy {'select_one': 'xyz'} format might
                # still be on kobo-prod
                _type_str = _expand_type_to_dict(_type.keys()[0])['type']
                _list_name = _type.values()[0]
                row.update({u'type': _type_str,
                            u'select_from_list_name': _list_name})
        for key in EXPANDABLE_FIELD_TYPES:
            if key in row and isinstance(row[key], basestring):
                row[key] = _expand_xpath_to_list(row[key])
        for (key, vals) in specials.iteritems():
            if key in row:
                _expand_translatable_content(content, row, key, vals)

        if REMOVE_EMPTY_STRINGS:
            for (key, val) in row.items():
                if val == "":
                    del row[key]

    # for now, prepend meta questions to the beginning of the survey
    # eventually, we may want to create a new "sheet" with these fields
    for row in _metas[::-1]:
        survey_content.remove(row)
        survey_content.insert(0, row)

    for row in content.get('choices', []):
        for (key, vals) in specials.iteritems():
            if key in row:
                _expand_translatable_content(content, row, key, vals)

    if 'settings' in content and isinstance(content['settings'], list):
        if len(content['settings']) > 0:
            content['settings'] = content['settings'][0]
        else:
            content['settings'] = {}
    content['schema'] = SCHEMA_VERSION


def expand_content(content, in_place=False):
    if in_place:
        expand_content_in_place(content)
        return None
    else:
        content_copy = deepcopy(content)
        expand_content_in_place(content_copy)
        return content_copy


def _get_special_survey_cols(content):
    '''This will extract information about columns in an xlsform with ':'s
    and give the "expand_content" information for parsing these columns.
    Examples--
        'media::image',
        'media::image::English',
        'label::Français',
        'hint::English',
    For more examples, see tests.
    '''
    uniq_cols = OrderedDict()
    special = OrderedDict()

    known_translated_cols = content.get('translated', [])

    def _pluck_uniq_cols(sheet_name):
        for row in content.get(sheet_name, []):
            # we don't want to expand columns which are already known
            # to be parsed and translated in a previous iteration
            _cols = filter(lambda r: r not in known_translated_cols,
                           row.keys())
            uniq_cols.update(OrderedDict.fromkeys(_cols))

    def _mark_special(**kwargs):
        column_name = kwargs.pop('column_name')
        special[column_name] = kwargs

    _pluck_uniq_cols('survey')
    _pluck_uniq_cols('choices')

    for column_name in uniq_cols.keys():
        if column_name in ['label', 'hint']:
            _mark_special(column_name=column_name,
                          column=column_name,
                          translation=UNTRANSLATED)
        if ':' not in column_name:
            continue
        if column_name.startswith('bind:'):
            continue
        if column_name.startswith('body:'):
            continue
        mtch = re.match('^media\s*::?\s*([^:]+)\s*::?\s*([^:]+)$', column_name)
        if mtch:
            matched = mtch.groups()
            media_type = matched[0]
            _mark_special(column_name=column_name,
                          column='media::{}'.format(media_type),
                          coltype='media',
                          media=media_type,
                          translation=matched[1])
            continue
        mtch = re.match('^media\s*::?\s*([^:]+)$', column_name)
        if mtch:
            media_type = mtch.groups()[0]
            _mark_special(column_name=column_name,
                          column='media::{}'.format(media_type),
                          coltype='media',
                          media=media_type,
                          translation=UNTRANSLATED)
            continue
        mtch = re.match('^([^:]+)\s*::?\s*([^:]+)$', column_name)
        if mtch:
            # example: label::x, constraint_message::x, hint::x
            matched = mtch.groups()
            column_shortname = matched[0]
            _mark_special(column_name=column_name,
                          column=column_shortname,
                          translation=matched[1])

            # also add the empty column if it exists
            if column_shortname in uniq_cols:
                _mark_special(column_name=column_shortname,
                              column=column_shortname,
                              translation=UNTRANSLATED)
            continue
    (translations,
     translated_cols) = _get_translations_from_special_cols(special,
                        content.get('translations', []))
    translated_cols.update(known_translated_cols)
    return (special, translations, sorted(translated_cols))


def _expand_type_to_dict(type_str):
    out = {}
    match = re.search('( or.other)$', type_str)
    if match:
        type_str = type_str.replace(match.groups()[0], '')
        out[OR_OTHER_COLUMN] = True
    match = re.search('select_(one|multiple)(_or_other)', type_str)
    if match:
        type_str = type_str.replace('_or_other', '')
        out[OR_OTHER_COLUMN] = True
    if type_str in ['select_one', 'select_multiple']:
        out['type'] = type_str
        return out
    for _re in [
                '^(select_one)\s+(\S+)$',
                '^(select_one_from_file)\s+(\S+)$',
                '^(select_multiple)\s+(\S+)$',
                '^(select_multiple_from_file)\s+(\S+)$',
                '^(select_one_external)\s+(\S+)$',
               ]:
        match = re.match(_re, type_str)
        if match:
            (type_, list_name) = match.groups()
            out['type'] = type_
            out['select_from_list_name'] = list_name
            return out
    # if it does not expand, we return the original string
    return {u'type': type_str}


def _expand_xpath_to_list(xpath_string):
    # a placeholder for a future expansion
    return xpath_string
