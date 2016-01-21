# -*- coding: utf-8 -*-
#
# This file is part of Flask-OAIServer
# Copyright (C) 2015 CERN.
#
# Flask-OAIServer is free software; you can redistribute it and/or
# modify it under the terms of the Revised BSD License; see LICENSE
# file for more details.

"""OAI-PMH verbs."""

from flask import request, render_template, g
import six
from datetime import (datetime, timedelta)
from flask import current_app as app
from uuid import uuid4
from invenio_oaiserver.sets import get_oai_records


def _fill_arguments_with_none(incoming, all_options=[]):
    for options in all_options:
        for option in options:
            if option not in incoming:
                incoming[option] = None


def _get_all_request_args():
    tmp_args_dict = {}
    for key, value in six.iteritems(request.args):
        tmp_args_dict[key] = value
    return tmp_args_dict


def _check_args(incoming, required, optional, exlusive):
    # TODO: include checking for duplicated arguments
    # TODO: check for more arguments passed
    g.verb = incoming["verb"]
    g.error = {}

    def _pop_arg_from_incoming(arg):
        try:
            return incoming.pop(arg)
        except KeyError:
            pass
        except:
            raise

    def _check_missing_required_args():
        if not set(required).issubset(set(incoming.keys())):
            missing_arguments = set(required) - set(incoming.keys())
            g.error["type"] = "badArgument"
            g.error["message"] = "You are missing required arguments: \
                                  {0}".format(missing_arguments)

    def _check_exclusiv_args():
        if set(exlusive).issubset(set(incoming.keys())):
            for arg in exlusive:
                _pop_arg_from_incoming(arg)
            if len(incoming):
                g.error["type"] = "badArgument"
                g.error["message"] = "You have passed too many arguments \
                                      together with EXLUSIVE argument."

    _pop_arg_from_incoming("verb")
    _check_missing_required_args()
    _check_exclusiv_args()


def identify():
    required_arg = []
    optional_arg = []
    exclusiv_arg = []
    incoming = _get_all_request_args()
    _check_args(incoming, required_arg, optional_arg, exclusiv_arg)
    if g.error:
        return render_template(
            "invenio_oaiserver/server/error.xml",
            incoming=incoming)
    else:
        return render_template("identify.xml")


def list_sets():
    from invenio_oaiserver.sets import (get_sets_list, get_sets_count)
    required_arg = []
    optional_arg = []
    exclusiv_arg = ["resumptionToken"]
    incoming = _get_all_request_args()
    _check_args(incoming, required_arg, optional_arg, exclusiv_arg)
    if g.error:
        return render_template("error.xml", incoming=incoming)
    else:
        sets = get_sets_list()
        resumption_token = {}
        if sets.count() < get_sets_count():
            resumption_token["coursor"] = app.config['CFG_SETS_MAX_LENGTH']
            resumption_token["date"] = datetime.strptime(
                g.response_date, "%Y-%m-%dT%H:%M:%Sz") + timedelta(
                hours=app.config['CFG_RESUMPTION_TOKEN_EXPIRE_TIME'])
            resumption_token["list_length"] = get_sets_count()
            # TODO: create a function to make a db entry on creation of the
            # resumption token
            resumption_token["token"] = uuid4()

        return render_template("list_sets.xml",
                               incoming=incoming,
                               sets=sets,
                               resumption_token=resumption_token)


def list_metadata_formats():
    required_arg = []
    optional_arg = ["identifier"]
    exclusiv_arg = []
    incoming = _get_all_request_args()
    _check_args(incoming, required_arg, optional_arg, exclusiv_arg)
    if g.error:
        return render_template("error.xml", incoming=incoming)
    else:
        print app.config['OAISERVER_METADATA_FORMATS']
        return render_template(
            "list_metadata_formats.xml",
            incoming=incoming,
            formats=app.config['OAISERVER_METADATA_FORMATS'])


# TODO differentiate with data passed fo list_records and list_identifiers
def list_records():
    required_arg = ["metadataPrefix"]
    optional_arg = ["from", "until", "set"]
    exclusiv_arg = ["resumptionToken"]
    incoming = _get_all_request_args()
    _check_args(incoming, required_arg, optional_arg, exclusiv_arg)
    _fill_arguments_with_none(incoming,
                              [required_arg,
                               optional_arg,
                               exclusiv_arg])
    if g.error:
        return render_template("error.xml", incoming=incoming)
    else:
        return render_template(
            "list_records.xml",
            incoming=incoming,
            records=get_oai_records(
                from_date=incoming['from'],
                until_date=incoming['until']))


def list_identifiers():
    required_arg = ["metadataPrefix"]
    optional_arg = ["from", "until", "set"]
    exclusiv_arg = ["resumptionToken"]
    incoming = _get_all_request_args()
    _check_args(incoming, required_arg, optional_arg, exclusiv_arg)
    _fill_arguments_with_none(incoming,
                              [required_arg,
                               optional_arg,
                               exclusiv_arg])
    if g.error:
        return render_template("error.xml", incoming=incoming)
    else:
        return render_template(
            "list_identifiers.xml",
            incoming=incoming,
            records=get_oai_records(
                from_date=incoming['from'],
                until_date=incoming['until']))


def get_record():
    required_arg = ["identifier", "metadataPrefix"]
    optional_arg = []
    exclusiv_arg = []
    incoming = _get_all_request_args()
    _check_args(incoming, required_arg, optional_arg, exclusiv_arg)
    if g.error:
        return render_template("error.xml", incoming=incoming)
    else:
        return "This is the requested record with {0} identifier in format \
                {1}".format(incoming["identifier"], incoming["metadatePrefix"])
