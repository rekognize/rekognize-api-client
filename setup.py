from setuptools import setup, find_packages


setup(
    name='rekognize',
    version='0.2',
    install_requires=(
        'requests>=1.2.3',
        'requests_oauthlib>=0.3.2',
    ),
    author='Onur Mat',
    author_email='onur@rekognize.io',
    license='MIT',
    url='https://github.com/rekognize/rekognize-api-client/',
    download_url='https://github.com/rekognize/rekognize-api-client/archive/master.zip',
    keywords='rekognize twitter api client',
    description='Rekognize Python Twitter API client',
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
        'Topic :: Internet',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
