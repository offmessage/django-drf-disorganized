"""
serializers.py
==============
"""

from rest_framework.serializers import HyperlinkedModelSerializer
from rest_framework.serializers import HyperlinkedModelSerializerOptions

from .encoder import UrlEncoder
from .relations import DisorganizedHyperlinkedIdentityField
from .relations import DisorganizedHyperlinkedRelatedField


class DisorganizedHyperlinkedSerializerOptions(HyperlinkedModelSerializerOptions):
    
    def __init__(self, meta):
        super(DisorganizedHyperlinkedSerializerOptions, self).__init__(meta)
        self.encoder = getattr(meta, 'encoder', UrlEncoder())
        
        
class DisorganizedHyperlinkedModelSerializer(HyperlinkedModelSerializer):
    
    _options_class = DisorganizedHyperlinkedSerializerOptions
    _hyperlink_field_class = DisorganizedHyperlinkedRelatedField
    _hyperlink_identify_field_class = DisorganizedHyperlinkedIdentityField

    def get_default_fields(self):
        fields = super(HyperlinkedModelSerializer, self).get_default_fields()

        if self.opts.view_name is None:
            self.opts.view_name = self._get_default_view_name(self.opts.model)
        
        if self.opts.url_field_name not in fields:
            url_field = self._hyperlink_identify_field_class(
                view_name=self.opts.view_name,
                lookup_field=self.opts.lookup_field,
                encoder=self.opts.encoder
            )
            ret = self._dict_class()
            ret[self.opts.url_field_name] = url_field
            ret.update(fields)
            fields = ret

        return fields

    def get_related_field(self, model_field, related_model, to_many):
        """
        Creates a default instance of a flat relational field.
        """
        kwargs = {
            'queryset': related_model._default_manager,
            'view_name': self._get_default_view_name(related_model),
            'many': to_many,
            'encoder': self.opts.encoder,
        }

        if model_field:
            kwargs['required'] = not(model_field.null or model_field.blank) and model_field.editable
            if model_field.help_text is not None:
                kwargs['help_text'] = model_field.help_text
            if model_field.verbose_name is not None:
                kwargs['label'] = model_field.verbose_name

        if self.opts.lookup_field:
            kwargs['lookup_field'] = self.opts.lookup_field

        return self._hyperlink_field_class(**kwargs)

