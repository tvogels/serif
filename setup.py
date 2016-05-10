from setuptools import setup, find_packages

setup(name='serif',
      version='0.1',
      description='Thijs\' typesetter',
      author='Thijs Vogels',
      author_email='t.vogels@me.com',
      url='https://github.com/tvogels/serif',
      license='MIT',
      install_requires=[
        'markdown',
        'mdx_outline',
        'PyExecJS',
        'Jinja2',
        'click',
        'pyyaml',
        'pygments',
      ],
      entry_points="""
        [console_scripts]
        serif=serif:cli
      """,
      dependency_links=[
        'https://github.com/tvogels/svgmath',
      ],
      packages=find_packages())