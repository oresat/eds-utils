from setuputils import setup
import eds_utils

with open('requirements.txt', 'r') as f:
    dependencies = f.readlines()

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='eds-utils',
    version=eds_utils.__version__,
    license='GPL-3.0',
    description='utils for editing CANopen EDS/DCF files',
    long_description=long_description,
    author='ryanpdx',
    author_email='tbd',
    maintainer='ryanpdx',
    maintainer_email='tbd',
    url='https://github.com/ryanpdx/eds-utils',
    packages=['eds_utils'],
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'eds2dcf = eds_utils.eds2dcf:eds2dcf',
            'eds-editor = eds_utils.eds_editor:eds_editor',
            'validate-eds = eds_utils.validate_eds:validate_eds',
        ],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Embedded Systems',
    ],
)
