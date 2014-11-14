"""
relations.py
============
"""

from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet

from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.relations import HyperlinkedRelatedField
from rest_framework.reverse import reverse

from .encoder import UrlEncoder


class DisorganizedHyperlinkedRelatedField(HyperlinkedRelatedField):
    """
    This field type only works with numeric id fields, and assumes pk
    """
    
    def get_url(self, obj, view_name, request, format):
        encoder = UrlEncoder(key=obj._meta.verbose_name)
        lookup = getattr(obj, self.lookup_field)
        kwargs = {self.lookup_field: encoder.encode_url(lookup)}
        return reverse(view_name, kwargs=kwargs, request=request, format=format)

    def get_object(self, queryset, view_name, view_args, view_kwargs):
        if not isinstance(queryset, QuerySet):
            raise TypeError("Cannot use Disorganized classes on non-model based views")
        lookup = view_kwargs.get(self.lookup_field, None)
        pk = view_kwargs.get(self.pk_url_kwarg, None)
        encoder_key = queryset.model._meta.verbose_name
        encoder = UrlEncoder(key=encoder_key)
        if lookup is not None:
            filter_kwargs = {self.lookup_field: encoder.decode_url(lookup)}
        elif pk is not None:
            filter_kwargs = {'pk': encoder.decode_url(pk)}
        else:
            raise ObjectDoesNotExist()

        return queryset.get(**filter_kwargs)


class DisorganizedHyperlinkedIdentityField(HyperlinkedIdentityField):
    """
    This field type only works with numeric id fields, and assumes pk
    """
    
    def __init__(self, *args, **kwargs):
        try:
            self.encoder = kwargs.pop('encoder')
        except KeyError:
            msg = "DisorganizedHyperlinkedIdentityField requires 'encoder' argument"
            raise ImproperlyConfigured(msg)
        super(DisorganizedHyperlinkedIdentityField, self).__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, format):
        lookup = getattr(obj, self.lookup_field, None)
        kwargs = {self.lookup_field: self.encoder.encode_url(lookup)}

        # Handle unsaved object case
        if lookup is None:
            return None

        return reverse(view_name, kwargs=kwargs, request=request, format=format)
    