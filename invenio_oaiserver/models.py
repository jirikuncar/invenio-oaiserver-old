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

"""Models for storing information about OAIServer state."""

from flask_babelex import lazy_gettext as _
from invenio_db import db
from sqlalchemy import ForeignKey, func
from sqlalchemy_utils import Timestamp


class OAISet(db.Model, Timestamp):
    """Information about OAI set."""

    __tablename__ = 'oaiserver_set'

    spec = db.Column(
        db.String(40),
        primary_key=True,
        info=dict(
            label=_('Identifier'),
            description=_('Identifier of the set.'),
        )
    )
    """Set identifier."""

    name = db.Column(
        db.String(40),
        info=dict(
            label=_('Long name'),
            description=_('Long name of the set.'),
        )
    )
    """Human readable name of the set."""

    description = db.Column(
        db.Text,
        nullable=True,
        info=dict(
            label=_('Description'),
            description=_('Description of the set.'),
        ),
    )
    """Human readable description."""

    search_pattern = db.Column(
        db.Text(),
        default=u'',
        info=dict(
            label=_('Search pattern'),
            description=_('Search pattern to select records'),
        )
    )
    """Search pattern to get records."""

    parent_name = db.Column(
        db.String(40),
        ForeignKey('oaiserver_set.spec'),
        nullable=True,
    )

    parent = db.relationship(
        'OAISet',
        remote_side=[spec],
        backref=db.backref('children', remote_side=[parent_name]),
        cascade='all, delete-orphan',
        single_parent=True,
    )

    @property
    def full_spec(self):
        if self.parent_name:
            return self.parent.full_spec + ':' + self.spec
        else:
            return self.spec


__all__ = ('Set', )
