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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'Django>=2.2,<4',
        'requests_oauthlib',
    ],
    # pinning pytest because pytest-sugar doesn't work with pytest v5.4.0
    # https://github.com/Teemu/pytest-sugar/issues/187
    extras_require={
        'test': [
            'pytest==5.3.5',
            'pytest-cov',
            'pytest-sugar',
            'flake8==3.0.4',
            'requests_mock',
            'codecov',
            'twine',
            'wheel',
            'setuptools',
            'pytest-django',
            'requests-mock',
            'raven',
        ]
    }
)
