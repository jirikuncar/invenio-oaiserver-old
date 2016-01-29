# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
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

"""Test OAI response."""

from __future__ import absolute_import

from invenio_db import db
from invenio_records.api import Record

from invenio_oaiserver.models import OAISet
from invenio_oaiserver.response import NS_DC, NS_OAIDC, NS_OAIPMH, \
    listrecords, listsets


def test_listsets(app):
    """Test ListSets."""
    with app.test_request_context():
        with db.session.begin_nested():
            a = OAISet(spec='test', name='Test', description="test desc")
            db.session.add(a)

        tree = listsets()

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

        tree = listrecords(metadataPrefix='oai_dc')

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
