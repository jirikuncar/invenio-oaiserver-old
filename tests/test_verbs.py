# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Test OAI verbs."""

from __future__ import absolute_import

import os

from invenio_db import db
from lxml import etree

from invenio_oaiserver.models import OAISet
from invenio_oaiserver.response import listsets


def _xpath_errors(body):
    """Find errors in body."""
    return list(body.iter('{*}error'))


def test_no_verb(app):
    """Test response when no verb is specified."""
    with app.test_client() as c:
        result = c.get('/oai2d')
        tree = etree.fromstring(result.data)
        assert 'Missing data for required field.' in _xpath_errors(
            tree)[0].text


def test_wrong_verb(app):
    with app.test_client() as c:
        result = c.get('/oai2d?verb=Aaa')
        tree = etree.fromstring(result.data)

        assert 'This is not a valid OAI-PMH verb:Aaa' in _xpath_errors(
            tree)[0].text


def test_identify(app):
    with app.test_client() as c:
        result = c.get('/oai2d?verb=Identify')
        assert 200 == result.status_code


def test_identify_with_additional_args(app):
    with app.test_client() as c:
        result = c.get('/oai2d?verb=Identify&notAValidArg=True')
        tree = etree.fromstring(result.data)
        assert 'You have passed too many arguments.' == _xpath_errors(
            tree)[0].text


def test_list_sets(app):
    with app.test_client() as c:
        result = c.get('/oai2d?verb=ListSets')


def test_list_sets_long(app):
    with app.test_client() as c:
        result = c.get('/oai2d?verb=ListSets')


def test_listsets(app, monkeypatch):
    """Test ListSets."""
    path = os.path.dirname(__file__)
    with open("{0}/demo_listsets.xml".format(path)) as myfile:
        expect = myfile.read().replace('\n', '')

    monkeypatch.setattr('invenio_oaiserver.response.datetime_to_datestamp',
                        lambda x: "2016-01-28T12:45:48Z")

    with app.test_request_context():
        with db.session.begin_nested():
            a = OAISet(spec='test', name='Test', description="test desc")
            db.session.add(a)

        assert expect == etree.tostring(listsets()).decode('utf-8')


def test_list_sets_with_resumption_token(app):
    pass


def test_list_sets_with_second_resumption_token(app):
    pass


def test_list_sets_with_resumption_token_and_other_args(app):
    pass
