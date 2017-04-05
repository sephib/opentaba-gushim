# OSMnx
# See full license in LICENSE.txt

from setuptools import setup

# provide a long description using reStructuredText
long_description = """
This project is aimed to generate geojson and topojson files from csv that MAPI distribtues

.. _GitHub: https://github.com/sephib/opentaba-gushim
"""

# list of classifiers from the PyPI classifiers trove
classifiers=['Development Status :: Development',
             'License :: OSI Approved :: MIT License',
             'Operating System :: OS Independent',
             'Intended Audience :: Science/Research',
             'Topic :: Scientific/Engineering :: GIS',
             'Topic :: Scientific/Engineering :: Visualization',
             'Programming Language :: Python',
             'Programming Language :: Python :: 2.7']


# now call setup
setup(name='gushim',
      version='0.1.dev',
      description='Generate gushim geo/topojson files from mapi csv files',
      long_description=long_description,
      classifiers=classifiers,
      url='https://github.com/sephib/opentaba-gushim',
      author='Sephi Berry',
      author_email='js.berry@gmail.com',
      license='MIT',
      platforms='any',
      data_files=[('', ['LICENSE.txt'])],
      install_requires=['requests>=2.11',
                        'numpy>=1.11',
                        'pandas>=0.19',
                        'geopandas>=0.2.1',
                        'Shapely>=1.5',
                        'PyYAML>=3.12',
                        # 'topojson>=0.2.0'
                        ],

      )

