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

    def test_task_loops(self):
        a = Task("a")
        b = Task("b")
        c = Task("c") 
        b.add_prereq(a)
        c.add_prereq(b)
        try:
            a.add_prereq(c)
            self.fail("Shouldn't have allowed a loop")
        except ValueError, e:
            pass

