from setuptools import setup, find_packages
from Cython.Distutils import build_ext


setup(
	maintainer='Daniel T. Andreasen',
    name='plotter',
	version=0.1,
	long_description=open('README.md').read(),
	license='MIT',
    packages=find_packages(),
    url='https://github.com/DanielAndreasey/synthesis-plotter',
    cmdclass={'build_ext': build_ext},
	install_requires=[
		'numpy>=1.15.0',
		'matplotlib>=2.0.2',
		'pandas>=0.23.0',
		'cython'
	],
	scripts=['src/plotter.py']
)
