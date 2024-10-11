import io
import os
from setuptools import find_packages, setup


here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    README = '\n' + f.read()

setup(
    name='drf-multitokenauth',
    version=os.getenv('PACKAGE_VERSION', '2.1.0').replace('refs/tags/', ''),
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    install_requires=[
        'django-ipware==3.0.*',
    ],
    include_package_data=True,
    license='BSD License',
    description='An extension of django rest frameworks token auth, providing multiple authentication tokens per user',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/anexia/drf-multitokenauth',
    author='Harald Nezbeda',
    author_email='hnezbeda@anexia-it.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Framework :: Django :: 5.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
