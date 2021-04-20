__author__ = 'samantha'
from setuptools import setup, find_packages

setup(name='trading',
      version='0.1',
      description='crypto trading hackery',
      author='Samantha Atkins',
      author_email='sjatkins@gmail.com',
      license='MIT',
      packages=['trading'],
      entry_points={
          'console_scripts': ['kucoin24=trading.scripts:get_kucoin_top']
      },
      install_requires = ['requests', 'beautifulsoup4', 'pycoingecko'],
      zip_safe=False)
