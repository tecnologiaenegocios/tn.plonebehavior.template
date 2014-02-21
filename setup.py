from setuptools import setup, find_packages

version = '1.0'

setup(
    name='tn.plonebehavior.template',
    version=version,
    description='',
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
    ],
    keywords='',
    author='TN Tecnologia e Negocios',
    author_email='ed@tecnologiaenegocios.com.br',
    url='http://www.tecnologiaenegocios.com.br',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['tn', 'tn.plonebehavior'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Plone',
        'five.grok',
        'plone.app.relationfield',
        'plone.api',
        'plone.behavior',
        'plone.browserlayer',
        'plone.directives.form',
        'plone.formwidget.contenttree',
        'lxml',
    ],
    extras_require={
        'test': [
            'stubydoo',
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
