# This file mainly exists to allow python setup.py test to work.
import os
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "termsandconditions_demo.settings"
test_dir = os.path.dirname(__file__)
sys.path.insert(0, test_dir)

from django.test.utils import get_runner
from django.conf import settings


def run_tests():
    test_runner = get_runner(settings)
    failures = test_runner([], verbosity=1, interactive=True)
    sys.exit()


if __name__ == "__main__":
    run_tests()
