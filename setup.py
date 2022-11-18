import os
import ast
import re
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


def get_version():
    pattern = re.compile(r'__version__\s+=\s+(.*)')

    with open('authbroker_client/version.py', 'rb') as src:
        return str(ast.literal_eval(
            pattern.search(src.read().decode('utf-8')).group(1)
        ))


setup(
    name='django_staff_sso_client',
    version=get_version(),
    packages=find_packages(),
    url='https://github.com/uktrade/django-staff-sso-client/',
    author='Department for International Trade',
    include_package_data=True,
    license='MIT',
    description='Reusable Django app to facilitate gov.uk Staff Single Sign On',
    long_description=README,
    long_description_content_type='text/markdown',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Framework :: Django',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 4.0',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'Django>=3.0,<4.2',
        'requests_oauthlib',
    ],
    extras_require={
        'test': [
            'pytest==7.1.1',
            'pytest-cov',
            'pytest-django',
            'flake8==4.0.1',
            'requests_mock',
            'codecov',
            'build',
            'twine',
            'wheel',
            'setuptools',
            'requests-mock',
            'raven',
        ]
    }
)
