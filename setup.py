from setuptools import setup, find_packages


version = '1.0.1'

classifiers = """
Development Status :: 5 - Production/Stable
Environment :: Console
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: JavaScript
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3.3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
""".strip().splitlines()

long_description = (
    open('README.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')

setup(
    name='crimp',
    version=version,
    description="JavaScript (ES5) minifier",
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=classifiers,
    keywords='',
    author='Tommy Yu',
    author_email='tommy.yu@auckland.ac.nz',
    url='https://github.com/calmjs/crimp',
    license='mit',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'calmjs.parse>=1.1.1',
    ],
    entry_points={
        'console_scripts': [
            'crimp = crimp.runtime:main',
        ],
    },
    test_suite="crimp.tests.make_suite",
)
