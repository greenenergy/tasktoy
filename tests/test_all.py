#!/usr/bin/env python

import unittest
#, HTMLTestRunner

from test_tasks import TaskTestCase

if __name__ == '__main__':
    log_format = '%(asctime)s %(levelname)s: %(message)s'
    #slog.basicConfig(level=0, format=log_format)

    suite = unittest.makeSuite(TaskTestCase,'test')

    #s2 = unittest.makeSuite(TwoPlayerHoldem,'test')
    #suite.addTest(s2)


    # Verbosity from 0 to 2
    # 0 - Only output final result
    # 1 - Output a [\.EF] for each test
    # 2 - Output the name and result for each test

    verbosity = 1
    do_html = False
    if do_html:
        runner = HTMLTestRunner.HTMLTestRunner(verbosity=verbosity)
    else:
        runner = unittest.TextTestRunner(verbosity=verbosity)
    runner.run(suite)

