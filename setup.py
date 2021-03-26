__author__ = 'samantha'
from setuptools import setup, find_packages

setup(name='cwutils',
      version='0.1',
      description='crypto trading hackery',
      author='Samantha Atkins',
      author_email='sjatkins@gmail.com',
      license='MIT',
      packages=['trading'],
      install_requires = ['requests', 'beautifulsoup4', 'pycoingecko'],
      zip_safe=False)
