# -*- coding: UTF-8 -*-
# Copyright 2009-2016 Luc Saffre
# License: BSD (see file COPYING for details)

"""
Defines the classes :class:`MenuItem` and :class:`Menu`
"""
from builtins import str
# import six
# str = six.text_type

from builtins import object

import logging
logger = logging.getLogger(__name__)

from django.conf import settings

from lino.core.utils import obj2str
from lino.core.actors import resolve_action
from lino.core.boundaction import BoundAction


class MenuItem(object):
    """A menu item. Note that this is subclassed by :class:`Menu`: a menu
    is also a menu item.

    """
    HOTKEY_MARKER = '~'

    name = None
    parent = None

    def __init__(self,
                 name=None, label=None, doc=None, enabled=True,
                 action=None,
                 #~ can_view=None,
                 hotkey=None,
                 params={},
                 help_text=None,
                 #~ request=None,
                 instance=None,
                 javascript=None,
                 href=None):
        if action is None:
            pass
            #~ if instance is not None:
                #~ action = instance.get_default_table().default_action
        elif not isinstance(action, BoundAction):
            raise Exception("20121003 not a BoundAction: %r" % action)
        if instance is not None:
            if action is None:
                raise Exception("20130610")
            instance._detail_action = action
        self.bound_action = action
        self.params = params
        self.href = href
        #~ self.request = request
        self.instance = instance
        self.javascript = javascript
        self.help_text = help_text

        if label is None:
            if instance is not None:
                label = str(instance)
            elif action is not None:
                label = action.get_button_label()

        if name is not None:
            self.name = name
        self.doc = doc
        self.enabled = enabled
        self.hotkey = hotkey

        if label:
            label = label.replace('~', '')
        self.label = label

        #~ if self.label is None:
            #~ raise Exception("20130907 %r has no label" % self)

    def compress(self):
        pass

    def getLabel(self):
        return self.label

    def getDoc(self):
        return self.doc

    def walk_items(self):
        yield self

    def __repr__(self):
        s = self.__class__.__name__ + "("
        attrs = []
        for k in 'label instance bound_action href params name'.split():
            v = getattr(self, k)
            if v is not None:
                attrs.append(k + "=" + obj2str(v))
        s += ', '.join(attrs)
        return s + ")"

    #~ def interesting(self,**kw):
        #~ l = []
        #~ if self.label is not None:
            #~ l.append(('label',self.label.strip()))
        #~ if not self.enabled:
            #~ l.append( ('enabled',self.enabled))
        #~ return l

    #~ def parents(self):
        #~ l = []
        #~ p = self.parent
        #~ while p is not None:
            #~ l.append(p)
            #~ p = p.parent
        #~ return l

    def get_url_path(self):
        if self.action:
            return str(self.action)
        if self.parent:
            s = self.parent.get_url_path()
            if len(s) and not s.endswith("/"):
                s += "/"
        else:
            s = '/'
        if self.name:
            return s + self.name
        return s

    def as_rst(self, ar, level=None):
        """
        Render this menu item as an rst string.
        Currently used only for writing test cases.
        """
        return str(self.label)

    def has_items(menu):
        for i in menu.items:
            if i.label is None:
                raise Exception("20130907 %r has no label" % i)
            if not i.label.startswith('-'):
                return True
        return False


def create_item(spec, action=None, help_text=None, **kw):
    """
    """
    a = resolve_action(spec, action)
    if help_text is None:
        if a == a.actor.default_action:
            help_text = a.actor.help_text or a.action.help_text
        else:
            help_text = a.action.help_text
    if help_text is not None:
        kw.update(help_text=help_text)
    kw.update(action=a)
    return MenuItem(**kw)


class Menu(MenuItem):

    """
    Represents a menu. A menu is conceptually a :class:`MenuItem`
    which contains other menu items.
    """

    avoid_lonely_items = False
    """
    If set to True, avoid lonely menu items by lifting them up one level.
    This is not done for top-level menus
    
    For example the following menu::
        
        Foo           Bar         Baz
        |Foobar       |BarBaz
         |Copy
         |Paste
        |FooBarBaz
         | Insert
         
    would become::
         
        Foo           BarBaz        Baz
        |Foobar       
         |Copy
         |Paste
        |Insert
         
    
    """

    def __init__(self, user_profile, name, label=None, parent=None, **kw):
        MenuItem.__init__(self, name, label, **kw)
        self.parent = parent
        self.user_profile = user_profile
        self.clear()

    def clear(self):
        self.items = []
        self.items_dict = {}

    def compress(self):
        """
        Dynamically removes empty menu entries.
        Collapses menu with only one item into their parent.
        """
        for mi in self.items:
            mi.compress()

        newitems = []

        for mi in self.items:
            if isinstance(mi, Menu):
                if mi.has_items():
                    if not self.avoid_lonely_items:
                        newitems.append(mi)
                    elif len(mi.items) == 1:
                        if not mi.items[0].label.startswith('-'):
                            if self.parent is None:
                                newitems.append(mi)
                            else:
                                newitems.append(mi.items[0])
                    elif len(mi.items) > 1:
                        newitems.append(mi)
            else:
                newitems.append(mi)

        self.items = newitems

    def add_action(self, *args, **kw):
        mi = create_item(*args, **kw)
        return self.add_item_instance(mi)

    def add_instance_action(self, obj, **kw):
        """Add an action which displays the given database object instance in
        a detail form for editing.  Used e.g. for the
        :class:`lino.modlib.system.models.SiteConfig` object.

        """
        kw.update(instance=obj)
        da = kw.get('action', None)
        if da is None:
            da = obj.get_default_table().detail_action
            kw.update(action=da)
        return self.add_item_instance(MenuItem(**kw))

    def add_item(self, name, label, **kw):
        return self.add_item_instance(MenuItem(name, label, **kw))

    def add_separator(self, label='-', **kw):
        if len(self.items) > 0 and not self.items[-1].label.startswith('-'):
            return self.add_item_instance(MenuItem(None, label, **kw))

    def add_menu(self, name, label, **kw):
        return self.add_item_instance(Menu(
            self.user_profile, name, label, self, **kw))

    def get_item(self, name):
        return self.items_dict[name]

    #~ def add_url_button(self,url,label):
    def add_url_button(self, url, **kw):
        kw.update(href=url)
        return self.add_item_instance(MenuItem(**kw))
        #~ self.items.append(dict(
          #~ xtype='button',text=label,
          #~ handler=js_code("function() {window.location='%s';}" % url)))

    def add_item_instance(self, mi):
        """
        Adds the specified MenuItem to this menu after checking whether
        it has view permission.
        """
        assert isinstance(mi, MenuItem)
        mi.parent = self
        if mi.bound_action is not None:
            #~ if not mi.bound_action.actor.get_view_permission(self.user):
            if not mi.bound_action.get_view_permission(self.user_profile):
                return
            #~ logger.info("20130129 _add_item %s for %s",mi.label,self.user_profile)
        if mi.name is not None:
            old = self.items_dict.get(mi.name)
            if old is not None:
                if mi.label != old.label:
                    raise Exception(
                        "Menu item %r labelled %s cannot override existing label %s" %
                        (mi.name, mi.label, old.label))
                return old
            self.items_dict[mi.name] = mi
        self.items.append(mi)
        return mi

    #~ def get(self,name):
        #~ return self.items_dict.get(name)

    def walk_items(self):
        yield self
        for mi in self.items:
            for i in mi.walk_items():
                yield i

    #~ def unused_sort_items(self,front=None,back=None):
        #~ new_items = []
        #~ if front:
            #~ for name in front.split():
                #~ new_items.append(self.findItem(name))
        #~ back_items = []
        #~ if back:
            #~ for name in back.split():
                #~ back_items.append(self.findItem(name))
        #~ for i in self.get_items():
            #~ if not i in new_items + back_items:
                #~ new_items.append(i)
        #~ self.items = new_items + back_items
        #~ self.items_dict = {}
        #~ for i in self.items:
            #~ self.items_dict[i.name] = i

    def as_bootstrap_html(self, renderer, request, level=1):
        raise Exception("20150824 moved to TextRenderer.show_menu")

    def as_rst(self, ar, level=1):
        raise Exception("20150824 moved to TextRenderer.show_menu")


class Toolbar(Menu):
    """A top-level :class:`Menu`.

    """
    pass


def find_menu_item(spec):
    from lino.api import rt
    profile = rt.modules.users.UserProfiles.get_by_value('900')
    menu = settings.SITE.get_site_menu(settings.SITE.kernel, profile)
    for mi in menu.walk_items():
        if mi.bound_action == spec:
            return mi
    return None
