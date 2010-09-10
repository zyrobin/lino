#coding: utf8
## Copyright 2008-2010 Luc Saffre
## This file is part of the Lino project.
## Lino is free software; you can redistribute it and/or modify 
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
## Lino is distributed in the hope that it will be useful, 
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
## GNU General Public License for more details.
## You should have received a copy of the GNU General Public License
## along with Lino; if not, see <http://www.gnu.org/licenses/>.


from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^lino\.modlib\.fields\.KnowledgeField"])
add_introspection_rules([], ["^lino\.modlib\.fields\.PercentageField"])
add_introspection_rules([], ["^lino\.modlib\.fields\.MyDateField"])
add_introspection_rules([], ["^lino\.modlib\.fields\.MonthField"])
add_introspection_rules([], ["^lino\.modlib\.fields\.QuantityField"])


LANGUAGE_CHOICES = [ (k,_(v)) for k,v in settings.LANGUAGES ]


#~ LANGUAGE_CHOICES = (
  #~ ('en', _("English")),
  #~ ('de', _("German")),
  #~ ('fr', _("French")),
  #~ ('nl', _("Dutch")),
  #~ ('et', _("Estonian")),
#~ )

KNOWLEDGE_CHOICES = (
  (0, _("not at all")), # - gar nicht
  (1, _("a bit")), #  - ein bisschen
  (2, _("moderate")), #  - mittelmäßig
  (3, _("quite well")), #  - gut
  (4, _("very well")), #  - sehr gut
)

class LanguageField(models.CharField):
    def __init__(self, *args, **kw):
        defaults = dict(
            verbose_name=_("Language"),
            choices=LANGUAGE_CHOICES,
            max_length=2,
            #~ limit_to_choices=True,
            )
        defaults.update(kw)
        models.CharField.__init__(self,*args, **defaults)

class KnowledgeField(models.SmallIntegerField):
    def __init__(self, *args, **kw):
        defaults = dict(
            choices=KNOWLEDGE_CHOICES,
            max_length=1,
            blank=True,null=True,
            #~ limit_to_choices=True,
            )
        defaults.update(kw)
        models.SmallIntegerField.__init__(self,*args, **defaults)
  
class PercentageField(models.SmallIntegerField):
    def __init__(self, *args, **kw):
        defaults = dict(
            max_length=3,
            )
        defaults.update(kw)
        models.SmallIntegerField.__init__(self,*args, **defaults)
  
class MonthField(models.CharField):
    def __init__(self, *args, **kw):
        defaults = dict(
            max_length=10,
            )
        defaults.update(kw)
        models.CharField.__init__(self,*args, **defaults)
  
class PriceField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        defaults = dict(
            max_length=10,
            max_digits=10,
            decimal_places=2,
            )
        defaults.update(kwargs)
        super(PriceField, self).__init__(*args, **defaults)
        
    def formfield(self, **kwargs):
        fld = super(PriceField, self).formfield(**kwargs)
        # display size is smaller than full size:
        fld.widget.attrs['size'] = "6"
        fld.widget.attrs['style'] = "text-align:right;"
        return fld
        
class MyDateField(models.DateField):
        
    def formfield(self, **kwargs):
        fld = super(MyDateField, self).formfield(**kwargs)
        # display size is smaller than full size:
        fld.widget.attrs['size'] = "8"
        return fld
        
        
        
class QuantityField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        defaults = dict(
            max_length=5,
            max_digits=5,
            decimal_places=0,
            )
        defaults.update(kwargs)
        super(QuantityField, self).__init__(*args, **defaults)
        
    def formfield(self, **kwargs):
        fld = super(QuantityField, self).formfield(**kwargs)
        fld.widget.attrs['size'] = "3"
        fld.widget.attrs['style'] = "text-align:right;"
        return fld
        
