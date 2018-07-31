from setuptools import setup


setup(name='gsem',
      version='0.1.3',
      description='Command line extension manager for Gnome-Shell',
      url='https://github.com/andriykohut/gsem',
      author='Andriy Kogut',
      author_email='kogut.andriy@gmail.com',
      license='MIT',
      packages=['gsem'],
      keywords='gsem gnome gnome-shell extention manager',
      zip_safe=True,
      entry_points={
          'console_scripts': ['gsem=gsem.cli:main'],
      })
