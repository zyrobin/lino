#!/usr/bin/env python
import os
import sys

sys.path.insert(0,'../..')

if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = "tutorials.actors.settings"

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
