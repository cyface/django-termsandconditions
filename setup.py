from setuptools import setup, find_packages

setup(
    name="django-termsandconditions",
    version="1.2.12",
    url='https://github.com/cyface/django-termsandconditions',
    license='BSD',
    description="django-termsandconditions is a Django app that enables users to accept terms and conditions of a site.",
    long_description=open('README.rst').read(),

    author='Tim White',
    author_email='tim@cyface.com',

    packages=find_packages(exclude=('termsandconditions_demo', 'tests', 'devscripts')),
    include_package_data=True,
    zip_safe=False,
    install_requires=['django>=1.8.3', 'future>=0.15.2'],
    test_suite="termsandconditions_demo.run_tests.run_tests",

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
