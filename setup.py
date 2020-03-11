import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(

    name='sasa_db',

    version='0.1',

    author="Tim Luca Turan",

    author_email="timturan@web.de",

    description="Utility to convert Excel tables to a sqlite database and access the data",

    long_description=long_description,

    long_description_content_type="text/markdown",

    url="https://github.com/TimLucaTuran/sasa_db",

    packages=['sasa_db'],

    license='MIT',

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
