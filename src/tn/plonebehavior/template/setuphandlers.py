from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from tn.plonebehavior.template import ITemplateConfiguration
from tn.plonebehavior.template import interfaces
from zope.lifecycleevent import ObjectModifiedEvent
from zope.event import notify

import zope.interface


def setupVarious(context):
    if context.readDataFile('tn.plonebehavior.template.marker.txt') is None:
        return

    portal = context.getSite()
    catalog = getToolByName(portal, 'portal_catalog')
    results = catalog(object_provides=interfaces.IPossibleTemplate.__identifier__)

    for brain in results:
        wrapped = brain.getObject()
        obj = aq_base(wrapped)
        if not ITemplateConfiguration(obj).xpath:
            zope.interface.noLongerProvides(obj, interfaces.IPossibleTemplate)
            notify(ObjectModifiedEvent(wrapped))
