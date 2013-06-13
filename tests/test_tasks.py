#!/usr/bin/env python

import unittest

from tasks import Task

class TaskTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_task_construction(self):
        t = Task("one")

