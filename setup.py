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

    include_package_data=True,

    install_requires=[
        'openpyxl',
        'scipy',
    ],

    classifiers=[

        "Programming Language :: Python :: 3",

        "License :: OSI Approved :: MIT License",

        "Operating System :: OS Independent",

    ],

)
