from setuptools import setup, find_packages
from grakeneval import __version__

setup(
  name='graken-eval',
  version=__version__,
  description='Graph evaluation',
  author='Thomas Trautner',
  author_email='t.trautner@hotmail.com',
  keywords = 'cli',
  packages=find_packages(),
  license='GPLv3',
  entry_points = {
    'console_scripts': [
      'graken-eval=grakeneval.cli:main'
    ],
  },
)
