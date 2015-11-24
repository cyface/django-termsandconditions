from setuptools import setup, find_packages

setup(
    name="django-termsandconditions",
    version="0.1.7",
    url='http://timlwhite.com',
    license='BSD',
    description="django-termsandconditions enables users to accept terms and conditions of a site.",
    long_description=open('README.rst').read(),

    author='Tim White',
    author_email='tim@cyface.com',

    packages=find_packages(exclude=('termsandconditions_demo', 'tests', 'devscripts')),
    include_package_data=True,
    zip_safe=False,

    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
