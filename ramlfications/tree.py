#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function


try:
    from collections import OrderedDict
except ImportError:  # pragma: no cover
    from ordereddict import OrderedDict  # pragma: no cover

import sys

from termcolor import colored

from .parser import APIRoot


COLOR_MAP = {
    "light": (('white', None),
              ('yellow', None),
              ('green', 'bold'),
              ('blue', 'bold'),
              ('cyan', 'bold')),
    "dark": (('grey', None),
             ('grey', 'bold'),
             ('grey', 'bold'),
             ('magenta', None),
             ('blue', None))
}


def _get_node_level(node, count):
    if node.parent:
        count += 1
        return _get_node_level(node.parent, count)
    else:
        return count


def _get_tree(api):
    resources = OrderedDict()
    # Can _resources be None? If yes, the next line crashes.
    # LR: hmm if resources are none, then no endpoints are defined in RAML
    # pretty much required
    # TODO: add validation if no resources are defined
    for r in api.resources:
        resources[r] = (r.method.upper(), r)

    return resources


def _order_resources(resources):
    #return OrderedDict(sorted(resources.items(), key=lambda t: t[0]))
    return resources


def _create_space(v):
    space_count = _get_node_level(v, count=0)
    space = "  " * space_count
    return space


def _set_ansi(string, screen_color, line_color):
    if screen_color:
        color, attr = COLOR_MAP[screen_color][line_color]
        if attr:
            return colored(string, color, attrs=[attr])
        return colored(string, color)
    return string


def _print_line(sp, msg, color, line_color):
    msg = "|" + sp + msg
    output = _set_ansi(msg, color, line_color) + "\n"
    sys.stdout.write(output)


def _return_param_type(node):
    params = OrderedDict()
    if node.query_params:
        params["Query Params"] = node.query_params
    if node.uri_params:
        params["URI Params"] = node.uri_params
    if node.form_params:
        params["Form Params"] = node.form_params
    return params


def _params(space, node, color, desc):
    params = _return_param_type(node)
    for k, v in list(params.items()):
        _print_line(space + '     ', k, color, 4)
        for p in v:
            if desc:
                desc = ": " + p.display_name
            else:
                desc = ''
            _print_line(space + '      ⌙ ',  p.name + desc, color, 4)  # NOQA


def _print_verbosity(ordered_resources, color, verbosity):
    for r in ordered_resources:
        space = _create_space(r)
        _print_line(space, "- " + r.path, color, 2)
        if verbosity > 0:
            _print_line(space, "  ⌙ " + r.method.upper(), color, 3)
            if verbosity > 1:
                desc = verbosity == 3
                _params(space, r, color, desc)


def _print_metadata(api, color):
    head = _set_ansi("=" * len(api.title), color, 0) + "\n"
    head += _set_ansi(api.title, color, 1) + "\n"
    head += _set_ansi("=" * len(api.title), color, 0) + "\n"
    head += _set_ansi("Base URI: " + api.base_uri, color, 1) + "\n"

    sys.stdout.write(head)


def pprint_tree(api, ordered_resources, print_color, verbosity):
    _print_metadata(api, print_color)
    _print_verbosity(ordered_resources, print_color, verbosity)


def ttree(load_obj, color, output, verbosity):  # pragma: no cover
    api = APIRoot(load_obj)
    resources = _get_tree(api)
    ordered_resources = _order_resources(resources)

    if output:
        sys.stdout = output  # file is opened via @click from __main__.py
        pprint_tree(api, ordered_resources, color, verbosity)
        output.close()
    else:
        pprint_tree(api, ordered_resources, color, verbosity)
