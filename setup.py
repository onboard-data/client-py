from distutils.core import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='api_sdk',
      version='0.1',
      description='Onboard API SDK',
      author='Luke Walsh',
      author_email='luke.walsh@onboarddata.io',
      url='https://www.onboarddata.io',
      packages=['api_sdk'],
      install_requires=requirements,
      )
