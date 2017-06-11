from setuptools import setup

setup(
    name='exp_wrapper',
    version='1.2',
    author='Hayato Sasaki',
    packages=['exp_wrapper'],
    install_requires=['GitPython'],
    scripts=['src/experiment'],
    package_dir={'': 'src'}
)
