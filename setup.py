import os
from setuptools import find_packages, setup
from authbroker_client import __version__

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django_staff_sso_client',
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    license='',
    description='Reusable Django app to facilitate gov.uk Staff Single Sign On',
    long_description=README,
    url='https://gov.uk/',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'django',
        'requests_oauthlib',
        'raven',
    ]
)
