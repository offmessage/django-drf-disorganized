"""
relations.py
============
"""

from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.relations import HyperlinkedRelatedField
from rest_framework.reverse import reverse


class DisorganizedHyperlinkedRelatedField(HyperlinkedRelatedField):
    """
    This field type only works with numeric id fields, and assumes pk
    """
    
    def __init__(self, *args, **kwargs):
        try:
            self.encoder = kwargs.pop('encoder')
        except KeyError:
            raise ImproperlyConfigured("DisorganizedHyperlinkedRelatedField field requires 'encoder' kwarg")
        print "Related field", repr(self.encoder.key), self.encoder.alphabet[:10]
        super(DisorganizedHyperlinkedRelatedField, self).__init__(*args, **kwargs)
        
    def get_url(self, obj, view_name, request, format):
        lookup = getattr(obj, self.lookup_field)
        kwargs = {self.lookup_field: self.encoder.encode_url(lookup)}
        return reverse(view_name, kwargs=kwargs, request=request, format=format)

    def get_object(self, queryset, view_name, view_args, view_kwargs):
        print queryset
        lookup = view_kwargs.get(self.lookup_field, None)
        pk = view_kwargs.get(self.pk_url_kwarg, None)

        if lookup is not None:
            filter_kwargs = {self.lookup_field: self.encoder.decode_url(lookup)}
        elif pk is not None:
            filter_kwargs = {'pk': self.encoder.decode_url(pk)}
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
        print "Identity field", repr(self.encoder.key), self.encoder.alphabet[:10]
        super(DisorganizedHyperlinkedIdentityField, self).__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, format):
        lookup = getattr(obj, self.lookup_field, None)
        print "___________________"
        print lookup
        print obj
        print repr(self.encoder.key)
        print self.encoder.alphabet[:10]
        print self.encoder.encode_url(lookup)
        print "___________________"
        kwargs = {self.lookup_field: self.encoder.encode_url(lookup)}

        # Handle unsaved object case
        if lookup is None:
            return None

        return reverse(view_name, kwargs=kwargs, request=request, format=format)
        
        
