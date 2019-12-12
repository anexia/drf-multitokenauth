import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

VERSION = '1.3.3'

here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    README = '\n' + f.read()


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds...')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution...')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine...')
        os.system('twine upload dist/*')

        self.status('Pushing git tags...')
        os.system('git tag {0}'.format(VERSION))
        os.system('git push --tags')

        sys.exit()


setup(
    name='django-rest-multitokenauth',
    version=VERSION,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    install_requires=[
        'django-ipware==3.0.*',
    ],
    include_package_data=True,
    license='BSD License',
    description='An extension of django rest frameworks token auth, providing multiple authentication tokens per user',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/anexia-it/django-rest-multitokenauth',
    author='Harald Nezbeda',
    author_email='hnezbeda@anexia-it.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    # $ setup.py upload support.
    cmdclass={
        'upload': UploadCommand,
    },
)
