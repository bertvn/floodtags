# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

'''
with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()
'''
setup(
    name='importance_calculator',
    version='1.0',
    description='importance calculator for floodtags',
    #long_description=readme,
    author='Bert van Nimwegen',
    author_email='bertvnimwegen@gmail.com',
    #url='https://github.com/kennethreitz/samplemod',
    #license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
