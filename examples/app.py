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

r"""Minimal Flask application example for development.

Create database and tables:

.. code-block:: console

    $ cd examples
    $ flask -a app.py db init
    $ flask -a app.py db create

Load demo records from invenio-records (see
invenio_records/data/marc21/bibliographic.xml):

.. code-block:: console

    $ dojson do -i data/marc21/bibliographic.xml -l marcxml marc21 | \
        flask -a app.py records create

Mint the records:

.. code-block:: console

    $ flask -a app.py fixtures oaiserver

"""

from __future__ import absolute_import, print_function

import os

from flask import Flask
from flask_cli import FlaskCLI
from invenio_assets import InvenioAssets
from invenio_db import InvenioDB
from invenio_pidstore.minters import recid_minter
from invenio_records import InvenioRecords
from invenio_records.models import RecordMetadata
from sqlalchemy.orm.attributes import flag_modified

from invenio_oaiserver import InvenioOAIServer
from invenio_oaiserver.minters import oaiid_minter

# Create Flask application
app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI=os.getenv('SQLALCHEMY_DATABASE_URI',
                                      'sqlite:///app.db'),
    SERVER_NAME="app",
)
FlaskCLI(app)
InvenioAssets(app)
InvenioDB(app)
InvenioRecords(app)
InvenioOAIServer(app)


@app.cli.group()
def fixtures():
    """Initialize example data."""


@fixtures.command()
def oaiserver():
    """Initialize OAI-PMH server."""
    from invenio_db import db
    from invenio_oaiserver.models import OAISet
    from invenio_records.api import Record

    # create a OAI Set
    db.session.add(OAISet(spec='test', name='Test', description="test desc",
                          search_pattern="title:Test0"))
    db.session.commit()

    # create a record
    schema = {
        'type': 'object',
        'properties': {
            'title': {'type': 'string'},
            'field': {'type': 'boolean'},
        },
        'required': ['title'],
    }
    Record.create({'title': 'Test0', '$schema': schema})
    db.session.commit()

    # mint all records
    records = RecordMetadata.query.all()
    for record in records:
        recid_minter(record.id, record.json)
        oaiid_minter(record.id, record.json)
        flag_modified(record.model, 'json')

    db.session.commit()
