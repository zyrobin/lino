# -*- coding: UTF-8 -*-
# Copyright 2008-2014 Luc Saffre
# This file is part of the Lino project.
# Lino is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# Lino is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public License
# along with Lino; if not, see <http://www.gnu.org/licenses/>.

"""
"""

import logging
logger = logging.getLogger(__name__)

from django.db import models
from django.utils.translation import ugettext_lazy as _

from lino import dd
from lino import mixins
from lino.utils.xmlgen.html import E


# class UploadType(dd.BabelNamed):
class UploadType(dd.Model):
    """The type of an upload."""
    class Meta:
        abstract = dd.is_abstract_model('uploads.UploadType')
        verbose_name = _("Upload Type")
        verbose_name_plural = _("Upload Types")

    name = models.CharField(max_length=200, verbose_name=_('Name'))

    def __unicode__(self):
        return self.name


class UploadTypes(dd.Table):
    """The table with all existing upload types.

This usually is accessible via the `Configure` menu.
    """
    required = dd.required(user_level='admin')
    model = 'uploads.UploadType'
    column_names = "name *"
    order_by = ["name"]


class Upload(
        dd.Uploadable,
        dd.UserAuthored,
        dd.Controllable):

    class Meta:
        abstract = dd.is_abstract_model('uploads.Upload')
        verbose_name = _("Upload")
        verbose_name_plural = _("Uploads")

    type = dd.ForeignKey(
        "uploads.UploadType",
        blank=True, null=True)

    description = models.CharField(
        _("Description"), max_length=200, blank=True)

    def __unicode__(self):
        if self.description:
            s = self.description
        else:
            s = self.file.name
            i = s.rfind('/')
            if i != -1:
                s = s[i + 1:]
        if self.type:
            s = unicode(self.type) + ' ' + s
        return s


class Uploads(dd.Table):
    "Shows all Uploads"
    required = dd.required(user_level='admin')
    model = 'uploads.Upload'
    column_names = "file type user owner description *"

    detail_layout = """
    file user
    type description
    owner
    """

    insert_layout = """
    type
    description
    file
    user
    """


class UploadsByType(Uploads):
    master_key = 'type'
    column_names = "file description user * "


class UploadsByController(Uploads):
    "UploadsByController"
    required = dd.required()
    master_key = 'owner'
    column_names = "file type description user * "

    insert_layout = """
    file
    type
    description
    """

    slave_grid_format = 'summary'

    @classmethod
    def get_slave_summary(self, obj, ar):
        """Displays the uploads related to this controller as a list grouped
by uploads type.

Note that this also works on
:class:`lino_welfare.modlib.uploads.models.UploadsByClient`.

        """
        elems = []
        UploadType = dd.modules.uploads.UploadType
        # Upload = dd.modules.uploads.Upload
        types = []
        for ut in UploadType.objects.all():
            sar = self.request(
                master_instance=obj, known_values=dict(type=ut))
            files = []
            for m in sar:
                files.append(E.li(ar.obj2html(
                    m, m.remark or m.file.name), ' '))
            if len(files) > 0:
                types += [
                    E.p(unicode(ut), ': '),
                    E.ul(*files)]
            # else:
            #     types += [
            #         E.p(unicode(ut), ': '),
            #         ar.instance_action_button(obj.create_household)]
        if len(types) > 0:
            elems.append(E.ul(*types))
        return E.div(*elems)


class MyUploads(Uploads, mixins.ByUser):
    """Shows only my Uploads (i.e. those whose author is current user)."""
    required = dd.required()
    column_names = "file description user owner *"
    # order_by = ["modified"]


system = dd.resolve_app('system')


def setup_main_menu(site, ui, profile, m):
    m = m.add_menu("office", system.OFFICE_MODULE_LABEL)
    m.add_action('uploads.MyUploads')


def setup_config_menu(site, ui, profile, m):
    m = m.add_menu("office", system.OFFICE_MODULE_LABEL)
    m.add_action('uploads.UploadTypes')


def setup_explorer_menu(site, ui, profile, m):
    m = m.add_menu("office", system.OFFICE_MODULE_LABEL)
    m.add_action('uploads.Uploads')
