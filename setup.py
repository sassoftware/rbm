#
# Copyright (c) SAS Institute Inc.
#

from setuptools import setup, find_packages

requires = [
        'psycopg2',
        'pyramid',
        'pyramid_tm',
        'SQLAlchemy',
        'transaction',
        'zope.sqlalchemy',
        ]


setup(  name='upsrv',
        packages=find_packages(exclude=['upsrv_test*']),
        install_requires=requires,
        )
