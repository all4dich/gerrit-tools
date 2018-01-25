from setuptools import setup, find_packages

setup(
    name='gerrit-tools',
    zip_safe=False,
    description='Tools in order to get information from Gerrit instance',
    author='Sunjoo Park',
    author_email='all4dich@gmail.com',
    packages=['swtools'],
    package_dir={'': 'src'}
)
