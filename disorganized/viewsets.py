"""
viewsets.py
===========
"""

from django.http import Http404

from rest_framework.viewsets import ModelViewSet

from .encoder import UrlEncoder


class DisorganizedModelViewSet(ModelViewSet):
    
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        
        if pk is not None:
            encoder_key = self.serializer_class.Meta.model._meta.verbose_name
            encoder = UrlEncoder(key=encoder_key)
            searchfor = encoder.decode_url(pk)
            queryset = queryset.filter(pk=searchfor)
        
        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404("No %(verbose_name)s found matching the query" %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj
