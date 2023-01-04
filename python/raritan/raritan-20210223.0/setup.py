from setuptools import setup, find_packages


__author__ = "Dax Mickelson"
__author_email = "dmickels@cisco.com"
__license__ = "BSD"

setup(
    name="raritan",
    version="20210223.0",
    description="SDK for interacting with Raritan PDU APIs.",
    long_description="""SDK for interacting with Raritan PDU APIs.""",
    url="https://github.com/daxm/raritan-pdu-json-rpc",
    author=__author__,
    author_email=__author_email,
    license=__license__,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    keywords="raritan pdu",
    packages=find_packages(exclude=["docs", "tests*"]),
    install_requires=[],
    python_requires=">=3.6",
    package_data={"raritan": ["resources/*"]},
    data_files=None,
)
