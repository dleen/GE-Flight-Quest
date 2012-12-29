try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'GE Flight Project',
    'author': 'David & Cheryl',
    'url': 'None yet.',
    'download_url': 'Where to download it.',
    'author_email': 'My email.',
    'version': '0.1',
    'install_requires': ['nose', 'pandas', 'numpy'],
    'packages': ['geflight'],
    'scripts': [],
    'name': 'geflight'
}

setup(**config)