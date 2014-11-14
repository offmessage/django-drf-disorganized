"""
relations.py
============
"""

from django.core.exceptions import ObjectDoesNotExist

from rest_framework.relations import HyperlinkedIdentityField as DRFIdentify
from rest_framework.relations import HyperlinkedRelatedField as DRFRelated
from rest_framework.reverse import reverse


class HyperlinkedRelatedField(DRFRelated):
    """
    This field type only works with numeric id fields, and assumes pk
    """
    
    def __init__(self, *args, **kwargs):
        try:
            self.encoder = kwargs.pop('encoder')
        except KeyError:
            raise ValueError("NonSequentialHyperlinkedRelatedField field requires 'encoder' kwarg")
        super(HyperlinkedRelatedField, self).__init__(*args, **kwargs)
        
    def get_url(self, obj, view_name, request, format):
        lookup_field = getattr(obj, self.lookup_field)
        kwargs = {self.lookup_field: self.encoder.encode_url(lookup_field)}
        return reverse(view_name, kwargs=kwargs, request=request, format=format)

    def get_object(self, queryset, view_name, view_args, view_kwargs):
        lookup = view_kwargs.get(self.lookup_field, None)
        pk = view_kwargs.get(self.pk_url_kwarg, None)

        if lookup is not None:
            filter_kwargs = {self.lookup_field: self.encoder.decode_url(lookup)}
        elif pk is not None:
            filter_kwargs = {'pk': self.encoder.decode_url(pk)}
        else:
            raise ObjectDoesNotExist()

        return queryset.get(**filter_kwargs)


class HyperlinkedIdentityField(DRFIdentify):
    """
    This field type only works with numeric id fields, and assumes pk
    """
    
    def __init__(self, *args, **kwargs):
        try:
            self.encoder = kwargs.pop('encoder')
        except KeyError:
            msg = "NonSequentialHyperlinkedIdentityField requires 'encoder' argument"
            raise ValueError(msg)
        super(HyperlinkedIdentityField, self).__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, format):
        lookup_field = getattr(obj, self.lookup_field, None)
        kwargs = {self.lookup_field: self.encoder.encode_url(lookup_field)}

        # Handle unsaved object case
        if lookup_field is None:
            return None

        return reverse(view_name, kwargs=kwargs, request=request, format=format)
        
        
