import setuptools

setuptools.setup(

    name='sasa_db',

    version='0.1',

    author="Tim Luca Turan",

    author_email="timturan@web.de",

    description="Utility to convert Excel tables to a sqlite database and access the data",

    url="https://github.com/TimLucaTuran/meta-material-database",

    packages=['sasa_db'],

    license='MIT',

    install_requires=[
        'sqlite3',
        'openpyxl',
    ],

    package_data={'': ['license.txt']},

    include_package_data=True,

    classifiers=[

        "Programming Language :: Python :: 3",

        "License :: OSI Approved :: MIT License",

        "Operating System :: OS Independent",

    ],

)
