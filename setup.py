import os
import re
from setuptools import setup, find_packages

regexp = re.compile(r'.*__version__ = [\'\"](.*?)[\'\"]', re.S)

base_package = 'equator'
base_path = os.path.dirname(__file__)

init_file = os.path.join(base_path, 'src', 'equator', '__init__.py')
with open(init_file, 'r') as f:
    module_content = f.read()

    match = regexp.match(module_content)
    if match:
        version = match.group(1)
    else:
        raise RuntimeError(
            'Cannot find __version__ in {}'.format(init_file))

with open('README.rst', 'r') as f:
    readme = f.read()

with open('CHANGELOG.rst', 'r') as f:
    changes = f.read()

def parse_requirements(filename):
    ''' Load requirements from a pip requirements file '''
    with open(filename, 'r') as fd:
        lines = []
        for line in fd:
            line.strip()
            if line and not line.startswith("#"):
                lines.append(line)
    return lines

requirements = parse_requirements('requirements.txt')


if __name__ == '__main__':
    setup(
        name='equator',
        description='Set of tools for comparing complex objects',
        long_description='\n\n'.join([readme, changes]),
        license='BSD license',
        url='https://github.com/ivanovmg/equator',
        version=version,
        author='Maxim Ivanov',
        author_email='ivanovmg@gmail.com',
        maintainer='Maxim Ivanov',
        maintainer_email='ivanovmg@gmail.com',
        install_requires=requirements,
        keywords=['equator'],
        package_dir={'': 'src'},
        packages=find_packages('src'),
        zip_safe=False,
        classifiers=['Development Status :: 3 - Alpha',
                     'Intended Audience :: Developers',
                     'Programming Language :: Python :: 3.6']
    )
