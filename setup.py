import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "mailserver",
    version = "0.1alpha1",
    url = 'http://github.com/telenieko/django-mailserver',
    license = 'BSD',
    description = "Create mail services in Django.",
    long_description = read('README.rst'),
    author = 'Marc Fargas',
    author_email = 'telenieko@telenieko.com',
    packages = find_packages('src', exclude=('mailserver.testapp*', )),
    package_dir = {'': 'src'},
    install_requires = ['setuptools'],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
