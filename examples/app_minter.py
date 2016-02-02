# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
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

Install `uuid` package:

.. code-block:: console

    $ sudo apt-get -y install uuid

Create database and tables:

.. code-block:: console

    $ cd examples
    $ flask -a app_minter.py db init
    $ flask -a app_minter.py db create

Load demo records:

.. code-block:: console

    $ demomarc21nbrecs=$(grep -c '</record>' data/marc21/bibliographic.xml)
    $ dojson do -i data/marc21/bibliographic.xml -l marcxml marc21 | \
        flask -a app_minter.py records create \
        $(for i in $(seq 1 $demomarc21nbrecs); do echo "-i " $(uuid); done)

Mint the records:

.. code-block:: console

    $ flask -a app_minter.py fixtures oaiserver

"""

from __future__ import absolute_import, print_function

import os

from flask import Flask
from flask_cli import FlaskCLI
from invenio_assets import InvenioAssets
from invenio_db import InvenioDB, db
from invenio_pidstore import InvenioPIDStore
from invenio_records import InvenioRecords
from invenio_records.models import RecordMetadata
from invenio_pidstore.minters import recid_minter
from invenio_oaiserver.minters import oaiid_minter

from invenio_oaiserver import InvenioOAIServer

# Create Flask application
app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI=os.getenv('SQLALCHEMY_DATABASE_URI',
                                      'sqlite:///app_minter.db'),
    SERVER_NAME="app",
)
FlaskCLI(app)
InvenioAssets(app)
InvenioDB(app)
InvenioRecords(app)
InvenioPIDStore(app)
InvenioOAIServer(app)


@app.cli.group()
def fixtures():
    """Initialize example data."""


@fixtures.command()
def oaiserver():
    """Initialize OAI-PMH server."""
    records = RecordMetadata.query.all()
    for record in records:
        recid_minter(record.id, record.json)
        oaiid_minter(record.id, record.json)
        # mark record as modified
    db.session.commit()
