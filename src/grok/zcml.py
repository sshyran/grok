##############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Grok ZCML directives."""

from zope import interface
import zope.configuration.fields

import os

from zope import component
from zope import interface

from zope.component.interfaces import IDefaultViewName
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.configuration.config import ConfigurationMachine
from zope.app.component.site import LocalSiteManager

import martian
from martian import scan
from martian.error import GrokError

import grok
from grok import components, meta


class IGrokDirective(interface.Interface):
    """Grok a package or module."""

    package = zope.configuration.fields.GlobalObject(
        title=u"Package",
        description=u"The package or module to be analyzed by grok.",
        required=False,
        )

_bootstrapped = False
def bootstrap():
    component.provideAdapter(components.ModelTraverser)
    component.provideAdapter(components.ContainerTraverser)

    # register the name 'index' as the default view name
    component.provideAdapter('index',
                             adapts=(grok.Model, IBrowserRequest),
                             provides=IDefaultViewName)
    component.provideAdapter('index',
                             adapts=(grok.Container, IBrowserRequest),
                             provides=IDefaultViewName)
    # register a subscriber for when grok.Sites are added to make them
    # into Zope 3 sites
    component.provideHandler(
        addSiteHandler, adapts=(grok.Site, grok.IObjectAddedEvent))

    # now grok the grokkers
    martian.grok_module(scan.module_info_from_module(meta), the_module_grokker)

def addSiteHandler(site, event):
    sitemanager = LocalSiteManager(site)
    # LocalSiteManager creates the 'default' folder in its __init__.
    # It's not needed anymore in new versions of Zope 3, therefore we
    # remove it
    del sitemanager['default']
    site.setSiteManager(sitemanager)

# add a cleanup hook so that grok will bootstrap itself again whenever
# the Component Architecture is torn down.
def resetBootstrap():
    global _bootstrapped
    # we need to make sure that the grokker registry is clean again
    the_module_grokker.clear()
    _bootstrapped = False
from zope.testing.cleanup import addCleanUp
addCleanUp(resetBootstrap)

the_multi_grokker = martian.MetaMultiGrokker()
the_module_grokker = martian.ModuleGrokker(the_multi_grokker)

def skip_tests(name):
    return name in ['tests', 'ftests']

def grokDirective(_context, package):
    do_grok(package.__name__, _context)

def do_grok(dotted_name, config):
    global _bootstrapped
    if not _bootstrapped:
        bootstrap()
        _bootstrapped = True
    martian.grok_dotted_name(
        dotted_name, the_module_grokker, exclude_filter=skip_tests,
        config=config
        )
