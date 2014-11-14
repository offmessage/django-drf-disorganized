import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-drf-disorganized',
    version='0.0.1',
    packages=['disorganized'],
    include_package_data=True,
    license='Apache License, Version 2.0',
    description='An extension to Django Rest Framework to include non-sequential IDs.',
    long_description=README,
    url='https://github.com/offmessage/django-drf-disorganized',
    author='Andy Theyers',
    author_email='andy.theyers@isotoma.com',
    install_requires=['djangorestframework',],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache License 2.0',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
