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

from invenio_db import db
from invenio_pidstore.minters import recid_minter
from invenio_records.api import Record
from lxml import etree

from invenio_oaiserver.minters import oaiid_minter
from invenio_oaiserver.models import OAISet
from invenio_oaiserver.response import NS_DC, NS_OAIDC, NS_OAIPMH, \
    datetime_to_datestamp


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


def test_getrecord(app):
    schema = {
        'type': 'object',
        'properties': {
            'title': {'type': 'string'},
            'field': {'type': 'boolean'},
        },
        'required': ['title'],
    }
    with app.test_request_context():
        with db.session.begin_nested():
            record = Record.create({'title': 'Test0', '$schema': schema}).model
            recid_minter(record.id, record.json)
            pid = oaiid_minter(record.id, record.json)
            pid_value = pid.pid_value
            pid_updated = pid.updated

        db.session.commit()

        with app.test_client() as c:
            result = c.get(
                "/oai2d?verb=GetRecord&identifier={0}&metadataPrefix=oai_dc"
                .format(pid_value))
            assert 200 == result.status_code

            tree = etree.fromstring(result.data)

            namespaces = {'x': NS_OAIPMH}
            assert len(tree.xpath('/x:OAI-PMH', namespaces=namespaces)) == 1
            assert len(tree.xpath('/x:OAI-PMH/x:GetRecord',
                                  namespaces=namespaces)) == 1
            assert len(tree.xpath('/x:OAI-PMH/x:GetRecord/x:header',
                                  namespaces=namespaces)) == 1
            assert len(tree.xpath(
                '/x:OAI-PMH/x:GetRecord/x:header/x:identifier',
                namespaces=namespaces)) == 1
            identifier = tree.xpath(
                '/x:OAI-PMH/x:GetRecord/x:header/x:identifier/text()',
                namespaces=namespaces)
            assert identifier == [str(record.id)]
            datestamp = tree.xpath(
                '/x:OAI-PMH/x:GetRecord/x:header/x:datestamp/text()',
                namespaces=namespaces)
            assert datestamp == [datetime_to_datestamp(pid_updated)]
            assert len(tree.xpath('/x:OAI-PMH/x:GetRecord/x:metadata',
                                  namespaces=namespaces)) == 1


def test_identify_with_additional_args(app):
    with app.test_client() as c:
        result = c.get('/oai2d?verb=Identify&notAValidArg=True')
        tree = etree.fromstring(result.data)
        assert 'You have passed too many arguments.' == _xpath_errors(
            tree)[0].text


def test_list_sets(app):
    """Test ListSets."""
    with app.test_request_context():
        with db.session.begin_nested():
            a = OAISet(spec='test', name='Test', description="test desc")
            db.session.add(a)

        with app.test_client() as c:
            result = c.get('/oai2d?verb=ListSets')

        tree = etree.fromstring(result.data)

        namespaces = {'x': NS_OAIPMH}
        assert len(tree.xpath('/x:OAI-PMH', namespaces=namespaces)) == 1

        assert len(tree.xpath('/x:OAI-PMH/x:ListSets',
                              namespaces=namespaces)) == 1
        assert len(tree.xpath('/x:OAI-PMH/x:ListSets/x:set',
                              namespaces=namespaces)) == 1
        assert len(tree.xpath('/x:OAI-PMH/x:ListSets/x:set/x:setSpec',
                              namespaces=namespaces)) == 1
        assert len(tree.xpath('/x:OAI-PMH/x:ListSets/x:set/x:setName',
                              namespaces=namespaces)) == 1
        assert len(tree.xpath(
            '/x:OAI-PMH/x:ListSets/x:set/x:setDescription',
            namespaces=namespaces
        )) == 1
        namespaces['y'] = NS_OAIDC
        assert len(
            tree.xpath('/x:OAI-PMH/x:ListSets/x:set/x:setDescription/y:dc',
                       namespaces=namespaces)
        ) == 1
        namespaces['z'] = NS_DC
        assert len(
            tree.xpath('/x:OAI-PMH/x:ListSets/x:set/x:setDescription/y:dc/'
                       'z:description', namespaces=namespaces)
        ) == 1
        text = tree.xpath(
            '/x:OAI-PMH/x:ListSets/x:set/x:setDescription/y:dc/'
            'z:description/text()', namespaces=namespaces)
        assert len(text) == 1
        assert text[0] == 'test desc'


def test_listrecords(app):
    """Test ListRecords."""
    schema = {
        'type': 'object',
        'properties': {
            'title': {'type': 'string'},
            'field': {'type': 'boolean'},
        },
        'required': ['title'],
    }
    with app.test_request_context():
        with db.session.begin_nested():
            Record.create({'title': 'Test0', '$schema': schema})

        with app.test_client() as c:
            result = c.get('/oai2d?verb=ListRecords&metadataPrefix=oai_dc')

        tree = etree.fromstring(result.data)

        namespaces = {'x': NS_OAIPMH}
        assert len(tree.xpath('/x:OAI-PMH', namespaces=namespaces)) == 1

        assert len(tree.xpath('/x:OAI-PMH/x:ListRecords',
                              namespaces=namespaces)) == 1
        assert len(tree.xpath('/x:OAI-PMH/x:ListRecords/x:record',
                              namespaces=namespaces)) == 1
        assert len(tree.xpath('/x:OAI-PMH/x:ListRecords/x:record/x:header',
                              namespaces=namespaces)) == 1
        assert len(tree.xpath('/x:OAI-PMH/x:ListRecords/x:record/x:header'
                              '/x:identifier', namespaces=namespaces)) == 1
        assert len(tree.xpath('/x:OAI-PMH/x:ListRecords/x:record/x:header'
                              '/x:datestamp', namespaces=namespaces)) == 1
        assert len(tree.xpath('/x:OAI-PMH/x:ListRecords/x:record/x:metadata',
                              namespaces=namespaces)) == 1


def test_list_sets_long(app):
    with app.test_client() as c:
        result = c.get('/oai2d?verb=ListSets')


def test_list_sets_with_resumption_token(app):
    pass


def test_list_sets_with_second_resumption_token(app):
    pass


def test_list_sets_with_resumption_token_and_other_args(app):
    pass
