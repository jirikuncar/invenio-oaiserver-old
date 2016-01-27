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

"""Sets helper functions."""

from flask import current_app
from .models import OAISet, SetRecord


def get_sets_list(starting_position=0, max_length=None):
    if not max_length:
        max_length = current_app.config['OAISERVER_SETS_MAX_LENGTH']

    sets = OAISet.query.offset(starting_position)
    if max_length:
        sets.limit(max_length)
    return sets

    # TODO: in batabase implementation this should not get all elements
    # return SETS[starting_position:starting_position+max_length]


def get_sets_count():
    return OAISet.query.count()


def get_oai_records(set_spec=None, from_date=None, until_date=None):
    setrecs = SetRecord.query.distinct(SetRecord.recid)
    if set_spec:
        setrecs = setrecs.filter(SetRecord.set_spec == set_spec)
    if from_date:
        setrecs = setrecs.filter(SetRecord.create_date >= from_date)
    if until_date:
        setrecs = setrecs.filter(SetRecord.create_date <= until_date)
    return setrecs
