from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open("README.md", "r") as f:
    long_description = f.read()

setup(name='onboard.client',
      version='1.7.1',
      author='Nathan Merritt',
      author_email='nathan.merritt@onboarddata.io',
      description='Onboard API SDK',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/onboard-data/client-py',
      packages=['onboard.client'],
      install_requires=requirements,
      package_data={
          'onboard.client': ['py.typed'],
      },
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      python_requires='>=3.7',
      )
