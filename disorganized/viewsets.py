"""
viewsets.py
===========
"""

from django.http import Http404

from rest_framework.viewsets import ModelViewSet


class DisorganizedModelViewSet(ModelViewSet):
    
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        
        if pk is not None:
            try:
                encoder = self.serializer_class.Meta.encoder
            except AttributeError:
                raise AttributeError("DisorganizedModelViewSet class requires an 'encoder' option")
            searchfor = encoder.decode_url(pk)
            queryset = queryset.filter(pk=searchfor)
        
        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404("No %(verbose_name)s found matching the query" %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj
