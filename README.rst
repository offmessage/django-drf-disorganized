================
DRF Disorganized
================

***Sadly this project has fallen well behind the fantastic progress made on Django Rest Framework and is not compatible with DRF 3.x. Please feel free to use it as a point of reference should you wish to achieve similar results yourself, but this project will no longer do it for you.***

It is considered best practice to not have guessable, sequential IDs
exposed by an API (for example see 
`Auto Increment Considered Harmful <http://joshua.schachter.org/2007/01/autoincrement>`_
by Joshua Schachter).

Unfortunately, the simple case of Django Rest Framework does exactly that. If
one uses ``HyperlinkedModelSerializer`` and ``ModelViewSet`` as outlined in the
examples and tutorials the URLs created are of the form::

  http://example.com/api/1.0/<resourcename>/1/
  http://example.com/api/1.0/<resourcename>/2/
  ...
  
This exposes the autoincremented IDs that Django uses by default on all models.

The long solution to this involves storing additional information (perhaps a
UUID) on the model and painstakingly wiring up the ``lookup_field`` parameters
on the various Serializer and ViewSet classes. This a) takes time, b) creates vast
amounts of boilerplate, c) carries a cognitive load whenever the developer
examines their code, and d) is boring to code and therefore error prone.

With this in mind **DRF Disorganized** provides alternatives to the standard
``HyperlinkedModelSerializer`` and ``ModelViewSet`` classes in the form of
*Disorganized* equivalents. These behave in exactly the same way as the DRF
classes, but the URLs they create are of the form::

  http://example.com/api/1.0/<resourcename>/<apparently_random_string>/
  http://example.com/api/1.0/<resourcename>/<apparently_random_string>/
  ...
  
The strings are in fact encoded IDs, each repeatably generatable, guaranteed
unique per serializer, and each Django model gets its own sequence (so the
curious can't guess URLs of one model by inspecting the URLs of another). And
best of all the DRF APIs all continue to work as expected.

It really is as simple as:

**serializers.py**::

    from disorganized.serializers import DisorganizedHyperlinkedModelSerializer
    
    class FooSerializer(DisorganizedHyperlinkedModelSerializer):
        
        class Meta:
            model = Foo
            
            
**views.py**::

    from disorganized.views import DisorganizedModelViewSet
    
    from .serializers import FooSerializer
    
    class FooViewSet(DisorganizedModelViewSet):
        queryset = Foo.objects.all()
        serializer_class = FooSerializer
        
        
