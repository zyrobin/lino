# -*- coding: UTF-8 -*-
# Copyright 2008-2017 Luc Saffre
# License: BSD (see file COPYING for details)

"""
Defines extended database field classes and utility functions
related to fields.
"""
from builtins import str
import six
from builtins import object

import logging
logger = logging.getLogger(__name__)

import datetime
from decimal import Decimal


from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.core.exceptions import ValidationError
from django.db.models.fields import NOT_PROVIDED

from lino.core.utils import resolve_field
from lino.core.utils import resolve_model
from lino.core.exceptions import ChangedAPI

from lino.utils import IncompleteDate
from lino.utils import quantities
from lino.utils.quantities import Duration

class PasswordField(models.CharField):

    """Stored as plain text in database, but not displayed in user
    interface.

    """
    pass


class RichTextField(models.TextField):

    """Like Django's `models.TextField`, but you can specify a keyword
    argument :attr:`textfield_format`.

    .. attribute:: textfield_format

        Override the global
        :attr:`lino.core.site.Site.textfield_format` setting.
    
        For backwards compatibility `format` is an alias for
        `textfield_format`.

    """

    def __init__(self, *args, **kw):
        self.textfield_format = kw.pop(
            'format', kw.pop('textfield_format', None))
        super(RichTextField, self).__init__(*args, **kw)

    def set_format(self, fmt):
        self.textfield_format = fmt


class PercentageField(models.DecimalField):

    """
    A field to express a percentage.
    The database stores this like a DecimalField.
    Plain HTML adds a "%".
    """

    def __init__(self, *args, **kwargs):
        defaults = dict(
            max_length=5,
            max_digits=5,
            decimal_places=2,
        )
        defaults.update(kwargs)
        super(PercentageField, self).__init__(*args, **defaults)


class DatePickerField(models.DateField):

    """
    A DateField that uses a DatePicker instead of a normal DateWidget.
    Doesn't yet work.
    """


class MonthField(models.DateField):

    """
    A DateField that uses a MonthPicker instead of a normal DateWidget
    """

    def __init__(self, *args, **kw):
        models.DateField.__init__(self, *args, **kw)


# def PriceField(*args, **kwargs):
#     defaults = dict(
#         max_length=10,
#         max_digits=10,
#         decimal_places=2,
#     )
#     defaults.update(kwargs)
#     return models.DecimalField(*args, **defaults)


class PriceField(models.DecimalField):
    """
    A thin wrapper around Django's `DecimalField
    <https://docs.djangoproject.com/en/1.11/ref/models/fields/#decimalfield>`_
    which adds default values for `decimal_places`, `max_length` and
    `max_digits`.
    """

    def __init__(self, *args, **kwargs):
        defaults = dict(
            max_length=10,
            max_digits=10,
            decimal_places=2,
        )
        defaults.update(kwargs)
        super(PriceField, self).__init__(*args, **defaults)


#~ class MyDateField(models.DateField):

    #~ def formfield(self, **kwargs):
        #~ fld = super(MyDateField, self).formfield(**kwargs)
        # ~ # display size is smaller than full size:
        #~ fld.widget.attrs['size'] = "8"
        #~ return fld


"""
http://stackoverflow.com/questions/454436/unique-fields-that-allow-nulls-in-django
answer Dec 20 '09 at 3:40 by mightyhal
http://stackoverflow.com/a/1934764
"""


# class NullCharField(models.CharField):  # subclass the CharField
#     description = "CharField that stores empty strings as NULL instead of ''."

#     def __init__(self, *args, **kwargs):
#         defaults = dict(blank=True, null=True)
#         defaults.update(kwargs)
#         super(NullCharField, self).__init__(*args, **defaults)

#     # this is the value right out of the db, or an instance
#     def to_python(self, value):
#         # ~ if isinstance(value, models.CharField): #if an instance, just return the instance
#         if isinstance(value, six.string_types):  # if a string, just return the value
#             return value
#         if value is None:  # if the db has a NULL (==None in Python)
#             return ''  # convert it into the Django-friendly '' string
#         else:
#             return value  # otherwise, return just the value

#     def get_db_prep_value(self, value, connection, prepared=False):
#         # catches value right before sending to db
#         # if Django tries to save '' string, send the db None (NULL)
#         if value == '':
#             return None
#         else:
#             return value  # otherwise, just pass the value


class FakeField(object):
    """
    Base class for :class:`RemoteField` and :class:`DisplayField`.
    """
    model = None
    db_column = None
    choices = []
    primary_key = False
    editable = False
    name = None
    serialize = False
    #~ verbose_name = None
    help_text = None
    preferred_width = 30
    preferred_height = 3
    max_digits = None
    decimal_places = None
    default = NOT_PROVIDED
    generate_reverse_relation = False  # needed when AFTER17
    remote_field = None
    sortable_by = None
    """
    A list of real fields to be used for sorting when this fake field
    is selected.  For remote fields this is set automatically, on
    virtual fields you can set it yourself.
    """

    # required by Django 1.8:
    is_relation = False
    concrete = False
    auto_created = False
    column = None
    empty_values = set([None, ''])
    
    # required by Django 1.10:
    one_to_many = False
    one_to_one = False

    # required since 20171003
    rel = None

    def is_enabled(self, lh):
        """
        Overridden by mti.EnableChild
        """
        return self.editable

    def clean(self, raw_value, obj):
        # needed for Django 1.8
        return raw_value

    def has_default(self):
        return self.default is not NOT_PROVIDED

    def get_default(self):
        return self.default
    
    def set_attributes_from_name(self, name):
        if not self.name:
            self.name = name
        self.attname = name
        self.column = None
        self.concrete = False
        # if self.verbose_name is None and self.name:
        #     self.verbose_name = self.name.replace('_', ' ')

class RemoteField(FakeField):
    """
    A field on a related object.

    Remote fields are created by
    :meth:`lino.core.model.Model.get_data_elem` when needed.

    .. attribute:: field

        The bottom-level field object.

    """
    #~ primary_key = False
    #~ editable = False

    def __init__(self, getter, name, fld, setter=None, **kw):
        self.func = getter
        self.name = name
        self.attname = name
        self.field = fld
        self.verbose_name = fld.verbose_name
        self.help_text = fld.help_text
        self.blank = fld.blank
        # self.null = getattr(fld, 'null', None)
        self.max_length = getattr(fld, 'max_length', None)
        self.max_digits = getattr(fld, 'max_digits', None)
        self.decimal_places = getattr(fld, 'decimal_places', None)
        self.sortable_by = [ name ]
        
        self.setter = setter
        if setter is not None:
            self.editable = True
            self.choices = getattr(fld, 'choices', None)
        #~ print 20120424, self.name
        #~ settings.SITE.register_virtual_field(self)

        if isinstance(fld, models.ForeignKey) or (isinstance(fld, VirtualField) and isinstance(fld.return_type, models.ForeignKey)):
            self.remote_field = self.field.remote_field
            from lino.core import store
            store.get_atomizer(self.remote_field, self, name)

    #~ def lino_resolve_type(self):
        #~ self._lino_atomizer = self.field._lino_atomizer
    def value_from_object(self, obj, ar=None):
        """
        Return the value of this field in the specified model instance
        `obj`.  `ar` may be `None`, it's forwarded to the getter
        method who may decide to return values depending on it.
        """
        m = self.func
        return m(obj, ar)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.value_from_object(instance)


class DisplayField(FakeField):
    """
    A field to be rendered like a normal read-only form field, but with
    plain HTML instead of an ``<input>`` tag.

    This is to be used as
    the `return_type` of a :class:`VirtualField`.

    The value to be represented is either some unicode text, a
    translatable text or a :mod:`HTML element <etgen.html>`.
    """
    choices = None
    blank = True
    drop_zone = None
    max_length = None

    def __init__(self, verbose_name=None, **kw):
        self.verbose_name = verbose_name
        for k, v in kw.items():
            assert hasattr(self, k)
            setattr(self, k, v)

    # the following dummy methods are never called but needed when
    # using a DisplayField as return_type of a VirtualField

    def to_python(self, *args, **kw):
        raise NotImplementedError(
            "%s.to_python(%s,%s)", (self.name, args, kw))

    def save_form_data(self, *args, **kw):
        raise NotImplementedError

    def value_to_string(self, *args, **kw):
        raise NotImplementedError

    def value_from_object(self, obj, ar=None):
        return self.default


class HtmlBox(DisplayField):
    """
    Like :class:`DisplayField`, but to be rendered as a panel rather
    than as a form field.
    """
    pass


# class VirtualGetter(object):
#     """A wrapper object for getting the content of a virtual field
#     programmatically.

#     """

#     def __init__(self, vf, instance):
#         self.vf = vf
#         self.instance = instance

#     def __call__(self, ar=None):
#         return self.vf.value_from_object(self.instance, ar)

#     # def __get__(self, instance, owner):
#     #     return self.vf.value_from_object(instance, None)

#     def __getattr__(self, name):
#         obj = self.vf.value_from_object(self.instance, None)
#         return getattr(obj, name)

#     def __repr__(self):
#         return "<{0}>.{1}".format(repr(self.instance), self.vf.name)

VFIELD_ATTRIBS = frozenset('''to_python choices save_form_data
  value_to_string max_length remote_field
  max_digits verbose_name decimal_places
  help_text blank'''.split())

class VirtualField(FakeField):
    """
    Represents a virtual field. Values of virtual fields are not stored
    in the database, but computed on the fly each time they get
    read. Django doesn't see them.

    A virtual field must have a `return_type`, which can be either a
    Django field type (CharField, TextField, IntegerField,
    BooleanField, ...) or one of Lino's custom fields
    :class:`DisplayField`, :class:`HtmlBox` or :class:`RequestField`.

    The `get` must be a callable which takes two arguments: `obj` the
    database object and `ar` an action request.

    The :attr:`model` of a VirtualField is the class where the field
    was *defined*. This can be an abstract model. The VirtualField
    instance does not have a list of the concrete models which use it
    (because they inherit from that class).
    """

    def __init__(self, return_type, get):
        self.return_type = return_type  # a Django Field instance
        self.get = get
        
        settings.SITE.register_virtual_field(self)
        """
        Normal VirtualFields are read-only and not editable.
        We don't want to require application developers to explicitly
        specify `editable=False` in their return_type::
        
          @dd.virtualfield(dd.PriceField(_("Total")))
          def total(self, ar=None):
              return self.total_excl + self.total_vat
        """

    def override_getter(self, get):
        self.get = get

    def attach_to_model(self, model, name):
        self.model = model
        self.name = name
        self.attname = name
        #~ self.return_type.name = name
        #~ self.return_type.attname = name
        #~ if issubclass(model,models.Model):
        #~ self.lino_resolve_type(model,name)
        
        # must now be done by caller code:
        # if AFTER17:
        #     model._meta.add_field(self, virtual=True)
        # else:
        #     model._meta.add_virtual_field(self)

        # if self.get is None:
        #     return
        # if self.get.func_code.co_argcount != 2:
        #     if self.get.func_code.co_argcount == 2:
        #         getter = self.get
        #         def w(fld, obj, ar=None):
        #             return getter(obj, ar)
        #         self.get = w
        #         logger.warning("DeprecationWarning")
        #     else:
        #         msg = "Invalid getter for VirtualField {}".format(self)
        #         raise ChangedAPI(msg)

        #~ logger.info('20120831 VirtualField %s.%s',full_model_name(model),name)

    def __repr__(self):
        if self.model is None:
            return super(VirtualField, self).__repr__()
        return "%s.%s.%s" % (self.model.__module__,
                             self.model.__name__, self.name)

    def lino_resolve_type(self):
        """Called on virtual fields that are defined on an Actor

        """
        #~ logger.info("20120903 lino_resolve_type %s.%s", actor_or_model, name)
        #~ if self.name is not None:
            #~ if self.name != name:
                #~ raise Exception("Tried to re-use %s.%s" % (actor_or_model,name))
        #~ self.name = name

        if isinstance(self.return_type, six.string_types):
            self.return_type = resolve_field(self.return_type)

        f = self.return_type
        #~ self.return_type.name = self.name
        if isinstance(f, models.ForeignKey):
            f.remote_field.model = resolve_model(f.remote_field.model)
            if f.verbose_name is None:
                #~ if f.name is None:
                f.verbose_name = f.remote_field.model._meta.verbose_name
                    #~ from lino.core.kernel import set_default_verbose_name
                    #~ set_default_verbose_name(self.return_type)

        if isinstance(f, FakeField):
            self.sortable_by = f.sortable_by
        # if self.name == 'detail_pointer':
        #     logger.info('20170905 resolve_type 1 %s on %s',
        #                 self.name, self.verbose_name)
            
        #~ removed 20120919 self.return_type.editable = self.editable
        for k in VFIELD_ATTRIBS:
            setattr(self, k, getattr(self.return_type, k, None))
        # if self.name == 'detail_pointer':
        #     logger.info('20170905 resolve_type done %s %s',
        #                 self.name, self.verbose_name)

        from lino.core import store
        #~ self._lino_atomizer = store.create_field(self,self.name)
        store.get_atomizer(self.model, self, self.name)


    def get_default(self):
        return self.return_type.get_default()
        #~

    def has_default(self):
        return self.return_type.has_default()

    def unused_contribute_to_class(self, cls, name):
        # if defined in abstract base class, called once on each submodel
        if self.name:
            if self.name != name:
                raise Exception("Attempt to re-use %s as %s in %s" % (
                    self.__class__.__name__, name, cls))
        else:
            self.name = name
            if self.verbose_name is None and self.name:
                self.verbose_name = self.name.replace('_', ' ')
        self.model = cls
        cls._meta.add_virtual_field(self)
        #~ cls._meta.add_field(self)

    def to_python(self, *args, **kwargs):
        return self.return_type.to_python(*args, **kwargs)

    #~ def save_form_data(self,*args,**kw): return self.return_type.save_form_data(*args,**kw)
    #~ def value_to_string(self,*args,**kw): return self.return_type.value_to_string(*args,**kw)
    #~ def get_choices(self): return self.return_type.choices
    #~ choices = property(get_choices)

    def set_value_in_object(self, request, obj, value):
        """
        Stores the specified `value` in the specified model instance
        `obj`.  `request` may be `None`.

        Note that any implementation must also return `obj`, and
        callers must be ready to get another instance.  This special
        behaviour is needed to implement
        :class:`lino.utils.mti.EnableChild`.
        """
        pass
        # if value is not None:
        #     raise NotImplementedError("Cannot write %s to field %s" %
        #                               (value, self))

    #~ def value_from_object(self,request,obj):
    def value_from_object(self, obj, ar=None):
        """
        Return the value of this field in the specified model instance
        `obj`.  `ar` may be `None`, it's forwarded to the getter
        method who may decide to return values depending on it.
        """
        m = self.get
        #~ print self.field.name
        # return m(self, obj, ar)
        return m(obj, ar)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.value_from_object(instance, None)
        # return VirtualGetter(self, instance)

    def __set__(self, instance, value):
        return self.set_value_in_object(None, instance, value)


def virtualfield(return_type):
    """
    Decorator to turn a method into a :class:`VirtualField`.
    """
    def decorator(fn):
        if isinstance(return_type, DummyField):
            return DummyField(fn)
        return VirtualField(return_type, fn)
    return decorator


class Constant(object):
    """
    Deserves more documentation.
    """

    def __init__(self, text_fn):
        self.text_fn = text_fn

def constant():
    """
    Decorator to turn a function into a :class:`Constant`.  The
    function must accept one positional argument `datasource`.
    """
    def decorator(fn):
        return Constant(fn)
    return decorator


class RequestField(VirtualField):
    """
    A :class:`VirtualField` whose values are table action requests to
    be rendered as a clickable integer containing the number of rows.
    Clicking on it will open a window with the table.
    """
    def __init__(self, get, *args, **kw):
        kw.setdefault('max_length', 8)
        VirtualField.__init__(self, DisplayField(*args, **kw), get)


def displayfield(*args, **kw):
    """
    Decorator to turn a method into a :class:`VirtualField` of type
    :class:`DisplayField`.
    """
    return virtualfield(DisplayField(*args, **kw))


def htmlbox(*args, **kw):
    """
    Decorator shortcut to turn a method into a a :class:`VirtualField`
    of type :class:`HtmlBox`.
    """
    return virtualfield(HtmlBox(*args, **kw))


def requestfield(*args, **kw):
    """
    Decorator shortcut to turn a method into a a :class:`VirtualField`
    of type :class:`RequestField`.
    """
    def decorator(fn):
        #~ def wrapped(*args):
            #~ return fn(*args)
        #~ return RequestField(wrapped,*args,**kw)
        return RequestField(fn, *args, **kw)
    return decorator


class CharField(models.CharField):
    """
    An extension around Django's `models.CharField`.

    Adds two keywords `mask_re` and `strip_chars_re` which, when using
    the ExtJS ui, will be rendered as the `maskRe` and `stripCharsRe`
    config options of `TextField` as described in the `ExtJS
    documentation
    <http://docs.sencha.com/extjs/3.4.0/#!/api/Ext.form.TextField>`__,
    converting naming conventions as follows:

    =============== ============ ==========================
    regex           regex        A JavaScript RegExp object to be tested against the field value during validation (defaults to null). If the test fails, the field will be marked invalid using regexText.
    mask_re         maskRe       An input mask regular expression that will be used to filter keystrokes that do not match (defaults to null). The maskRe will not operate on any paste events.
    strip_chars_re  stripCharsRe A JavaScript RegExp object used to strip unwanted content from the value before validation (defaults to null).
    =============== ============ ==========================


    Example usage:

      belgian_phone_no = dd.CharField(max_length=15,strip_chars_re='')
    """

    def __init__(self, *args, **kw):
        self.strip_chars_re = kw.pop('strip_chars_re', None)
        self.mask_re = kw.pop('mask_re', None)
        self.regex = kw.pop('regex', None)
        models.CharField.__init__(self, *args, **kw)


class QuantityField(CharField):
    """
    A field that accepts :class:`Quantity
    <lino.utils.quantities.Quantity>`, :class:`Percentage
    <lino.utils.quantities.Percentage>` and :class:`Duration
    <lino.utils.quantities.Duration>` values.

    Implemented as a CharField (sorting or filter ranges may not work
    as expected).

    When you set `blank=True`, then you should declare `null=True` as
    well.
    """
    description = _("Quantity (Decimal or Duration)")

    def __init__(self, *args, **kw):
        kw.setdefault('max_length', 6)
        models.Field.__init__(self, *args, **kw)
        if self.blank and not self.null:
            raise ChangedAPI(
                "When `blank` is True, `null` must be True as well.")
            
        #~ models.CharField.__init__(self,*args,**kw)

    #~ def get_internal_type(self):
        #~ return "CharField"

    def to_python(self, value):
        """
        Excerpt from `Django doc
        <https://docs.djangoproject.com/en/dev/howto/custom-model-fields/#django.db.models.Field.to_python>`__:

            As a general rule, the method should deal gracefully with
            any of the following arguments:

            - An instance of the correct type (e.g., Hand in our ongoing example).
            - A string (e.g., from a deserializer).
            - Whatever the database returns for the column type you’re using.

        I'd add "Any value specified for this field when instantiating
        a model."

        >>> to_python(None)
        >>> to_python(30)
        >>> to_python(30L)
        >>> to_python('')
        >>> to_python(Decimal(0))
        """
        if isinstance(value, Decimal):
            return value
        if value:
            if isinstance(value, six.string_types):
                return quantities.parse(value)
            return Decimal(value)
        return None

    def from_db_value(self, value, expression, connection, context):
        return quantities.parse(value) if value else self.get_default()

    # def get_db_prep_value(self, value, connection, prepared=False):
    #     return str(value) if value else ''
        
    def get_prep_value(self, value):
        # if value is None:
        #     return ''
        return str(value) if value else ''


class DurationField(QuantityField):
    """
    A field that stores :class:`Duration
    <lino.utils.quantities.Duration>` values as CHAR.

    Note that you cannot use SUM or AVG agregators on these fields
    since the database does not know how to calculate sums from them.
    """
    def from_db_value(self, value, expression, connection, context):
        return Duration(value) if value else self.get_default()

    def to_python(self, value):
        if isinstance(value, Duration):
            return value
        if value:
            # if isinstance(value, six.string_types):
            #     return Duration(value)
            return Duration(value)
        return None


def validate_incomplete_date(value):
    """Raise ValidationError if user enters e.g. a date 30.02.2009.
    """
    try:
        value.as_date()
    except ValueError:
        raise ValidationError(_("Invalid date"))


class IncompleteDateField(models.CharField):
    """
    A field that behaves like a DateField, but accepts incomplete
    dates represented using
    :class:`lino.utils.format_date.IncompleteDate`.
    """

    default_validators = [validate_incomplete_date]

    def __init__(self, *args, **kw):
        kw.update(max_length=11)
        # msgkw = dict()
        # msgkw.update(ex1=IncompleteDate(1980, 0, 0)
        #              .strftime(settings.SITE.date_format_strftime))
        # msgkw.update(ex2=IncompleteDate(1980, 7, 0)
        #              .strftime(settings.SITE.date_format_strftime))
        # msgkw.update(ex3=IncompleteDate(0, 7, 23)
        #              .strftime(settings.SITE.date_format_strftime))
        kw.setdefault('help_text', _("""\
Uncomplete dates are allowed, e.g. 
"00.00.1980" means "some day in 1980", 
"00.07.1980" means "in July 1980"
or "23.07.0000" means "on a 23th of July"."""))
        models.CharField.__init__(self, *args, **kw)

    def deconstruct(self):
        name, path, args, kwargs = super(IncompleteDateField, self).deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs

    # def get_internal_type(self):
    #     return "CharField"

    def from_db_value(self, value, expression, connection, context):
        return IncompleteDate.parse(value) if value else self.get_default()
        # if value:
        #     return IncompleteDate.parse(value)
        # return ''

    def to_python(self, value):
        if isinstance(value, IncompleteDate):
            return value
        if isinstance(value, datetime.date):
            #~ return IncompleteDate(value.strftime("%Y-%m-%d"))
            #~ return IncompleteDate(d2iso(value))
            return IncompleteDate.from_date(value)
        # if value:
        #     return IncompleteDate.parse(value)
        # return ''
        return IncompleteDate.parse(value) if value else ''

    # def get_prep_value(self, value):
    #     return str(value)

    def get_prep_value(self, value):
        return str(value) if value else ''
        # if value:
        #     return str(value)
        #     # return '"' + str(value) + '"'
        #     #~ return value.format("%04d%02d%02d")
        # return ''

    #~ def value_to_string(self, obj):
        #~ value = self._get_val_from_obj(obj)
        #~ return self.get_prep_value(value)


class Dummy(object):
    pass


class DummyField(FakeField):
    """
    Represents a field that doesn't exist in the current configuration
    but might exist in other configurations. The "value" of a
    DummyField is always `None`.

    See e.g. :func:`ForeignKey` and :func:`fields_list`.
    """
    # choices = []
    # primary_key = False

    def __init__(self, *args, **kw):
        pass
    
    # def __init__(self, name, *args, **kw):
    #     self.name = name

    def __str__(self):
        return self.name
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return None

    def get_default(self):
        return None

    def contribute_to_class(self, cls, name):
        self.name = name
        v = getattr(cls, name, NOT_PROVIDED)
        if v is not NOT_PROVIDED:
            msg = ("{0} cannot contribute to {1} because it has already "
                   "an attribute '{2}'.")
            msg = msg.format(self, cls, name)
            if settings.SITE.ignore_model_errors:
                logger.warning(msg)
            else:
                raise Exception(msg)
        setattr(cls, name, self)

    def set_attributes_from_name(self, k):
        pass

def wildcard_data_elems(model):
    """
    Yield names to be used as wildcard in the :attr:`column_names` of a
    table or when :func:`fields_list` finds a ``*``.
    """
    meta = model._meta
    for f in meta.fields:
        # if not isinstance(f, fields.RichTextField):
        if not isinstance(f, VirtualField):
            if not getattr(f, '_lino_babel_field', False):
                yield f
    for f in meta.many_to_many:
        yield f
    for f in meta.virtual_fields:
        #if not isinstance(f, VirtualField):
        yield f
    # todo: for slave in self.report.slaves


class RecurrenceField(models.CharField):
    """
    Deserves more documentation.
    """

    def __init__(self, *args, **kw):
        kw.setdefault('max_length', 200)
        models.CharField.__init__(self, *args, **kw)


def use_as_wildcard(de):
    if de.name.endswith('_ptr'):
        return False
    return True


def fields_list(model, field_names):
    """
    Return a set with the names of the specified fields, checking
    whether each of them exists.

    Arguments: `model` is any subclass of `django.db.models.Model`. It
    may be a string with the full name of a model
    (e.g. ``"myapp.MyModel"``).  `field_names` is a single string with
    a space-separated list of field names.

    If one of the names refers to a :class:`DummyField`, this name
    will be ignored silently.

    For example if you have a model `MyModel` with two fields `foo` and
    `bar`, then ``dd.fields_list(MyModel,"foo bar")`` will return
    ``['foo','bar']`` and ``dd.fields_list(MyModel,"foo baz")`` will raise
    an exception.

    TODO: either rename this to `fields_set` or change it to return an
    iterable on the fields.
    """
    lst = set()
    names_list = field_names.split()

    for name in names_list:
        if name == '*':
            explicit_names = set()
            for name in names_list:
                if name != '*':
                    explicit_names.add(name)
            for de in wildcard_data_elems(model):
                if not isinstance(de, DummyField):
                    if de.name not in explicit_names:
                        if use_as_wildcard(de):
                            lst.add(de.name)
        else:
            e = model.get_data_elem(name)
            if e is None:
                raise models.FieldDoesNotExist(
                    "No data element %r in %s" % (name, model))
            if isinstance(e, DummyField):
                pass
            else:
                lst.add(e.name)
    return lst


def pointer_factory(cls, othermodel, *args, **kw):
    """
    Instantiate a `ForeignKey` or `OneToOneField` with some subtle
    differences:

    - It supports `othermodel` being `None` or the name of some
      non-installed model and returns a :class:`DummyField` in that
      case.  This difference is useful when designing reusable models.

    - Explicitly sets the default value for `on_delete
      <https://docs.djangoproject.com/en/1.11/ref/models/fields/#django.db.models.ForeignKey.on_delete>`__
      to ``CASCADE`` (as required by Django 2).
    """
    if othermodel is None:
        return DummyField(othermodel, *args, **kw)
    if isinstance(othermodel, six.string_types):
        if not settings.SITE.is_installed_model_spec(othermodel):
            return DummyField(othermodel, *args, **kw)

    kw.setdefault('on_delete', models.CASCADE)
    return cls(othermodel, *args, **kw)

def OneToOneField(*args, **kwargs):
    """
    Instantiate a :class:`django.db.models.OneToOneField` using :func:`pointer_factory`.
    """
    return pointer_factory(models.OneToOneField, *args, **kwargs)

def ForeignKey(*args, **kwargs):
    """
    Instantiate a :class:`django.db.models.ForeignKey` using
    :func:`pointer_factory`.
    """
    return pointer_factory(models.ForeignKey, *args, **kwargs)


class CustomField(object):
    """
    Mixin to create a custom field.

    It defines a single method :meth:`create_layout_elem`.
    """
    def create_layout_elem(self, base_class, layout_handle, field, **kw):
        """Return the widget to represent this field in the specified
        `layout_handle`.

        The widget must be an instance of the given `base_class`.

        `self` and `field` are identical unless `self` is a
        :class`RemoteField` or a :class:`VirtualField`.

        """
        return None


class ImportedFields(object):
    """
    Mixin for models which have "imported fields".
    """
    _imported_fields = set()

    @classmethod
    def declare_imported_fields(cls, names):
        cls._imported_fields = cls._imported_fields | set(
            fields_list(cls, names))
        #~ logger.info('20120801 %s.declare_imported_fields() --> %s' % (
            #~ cls,cls._imported_fields))

