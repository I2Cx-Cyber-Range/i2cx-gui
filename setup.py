import setuptools

with open("README.md", "r",encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
     name='i2cx',  
     version='0.9.2',
     author="LOOTUS",
     author_email="julien.moinard@lootus.net",
     description="Graphical interface for I2Cx Cyber Range, scanner-Lite(FT2232H),scanner (FPGA) and platform (stm32F7) ",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/I2Cx-Cyber-Range/i2cx-gui",
     packages=["i2cx"],
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
         "Operating System :: OS Independent",
     ],
     python_requires='>=3.6',
       install_requires=[
        'pyside6',
        'pyftdi'
    ],
    keywords='ftdi i2cx pyside cyberrange IoT stm32 fpga lattice',
    project_urls={
        'Homepage': 'https://www.i2cx.io',
    },
    entry_points={
        'console_scripts': [
            'i2cx=i2cx:Cli'
        ],
    },
    setup_requires=['setuptools_scm'],
    include_package_data=True,
 )
