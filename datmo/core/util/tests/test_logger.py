#!/usr/bin/python
"""
Tests for logger.py
"""
import shutil
import os
import logging
from time import sleep
from datmo.core.util.logger import DatmoLogger


class TestLogger():
    def test_logger(self):
        logger = DatmoLogger.get_logger()
        logger.warning("testing")
        logger.error("WHAT?")
        assert logger.level == DatmoLogger().logging_level

    def test_datmo_logger_get_logfiles(self):
        if hasattr(logging, 'handlers'):
            files = DatmoLogger.get_logfiles()
            assert len(list(files)) > 0
            for f in files:
                assert DatmoLogger().logging_path in f

    def test_find_text_in_logs(self):
        if hasattr(logging, 'handlers'):
            logger = DatmoLogger.get_logger()
            logger.warning("can you find this")
            results = DatmoLogger.find_text_in_logs("can you find this")
            assert len(results) == 1
            for r in results:
                assert r["file"]
                assert r["line_number"]
                assert r["line"]

    def test_get_logger_should_return_same_logger(self):
        f = DatmoLogger.get_logger("foobar")
        f2 = DatmoLogger.get_logger("foobar")
        assert f == f2

    def test_multiple_loggers(self):
        if hasattr(logging, 'handlers'):
            l1 = DatmoLogger.get_logger("logger1")
            l2 = DatmoLogger.get_logger("logger2")
            l1.warning("pizza")
            l2.warning("party")
            assert len(DatmoLogger.find_text_in_logs("pizza")) == 1
            assert len(DatmoLogger.find_text_in_logs("logger2")) == 1

    def test_multiple_log_files(self):
        if hasattr(logging, 'handlers'):
            l1 = DatmoLogger.get_logger("logger3", "debug.txt")
            l2 = DatmoLogger.get_logger("logger3", "info.txt")
            l1.warning("green")
            l2.warning("purple")
            r = DatmoLogger.find_text_in_logs("green")
            assert len(r) == 1
            assert r[0]["file"].find("debug.txt")
            r = DatmoLogger.find_text_in_logs("purple")
            assert len(r) == 1
            assert r[0]["file"].find("info.txt")

    def test_autocreate_dir(self):
        if hasattr(logging, 'handlers'):
            log_path = os.path.join(os.path.expanduser("~"), '.datmo')
            shutil.rmtree(log_path)
            assert not os.path.exists(log_path)
            logger = DatmoLogger.get_logger("logger3", "new.txt")
            logger.warning("testing")
            assert len(DatmoLogger.find_text_in_logs("testing")) == 1
            default_logger = DatmoLogger.get_logger()
            default_logger.warning("default-logger")
            assert len(DatmoLogger.find_text_in_logs("default-logger")) == 1

    def test_timeit_decorator(self):
        # NOTE:  If this test is failing be sure to add
        # LOGGING_LEVEL=DEBUG before pytest
        # or add as an environment variable
        if hasattr(logging, 'handlers'):

            @DatmoLogger.timeit
            def slow_fn():
                sleep(1)

            slow_fn()
            assert len(DatmoLogger.find_text_in_logs("slow_fn")) == 1
