#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `PROFYLE_ingest` package."""


import unittest
from PROFYLE_ingest import create_repo

class TestProfyle_ingest(unittest.TestCase):
    """Tests for `PROFYLE_ingest` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        # some nonsese to make sure the profile gets used:
        self._attrs = create_repo.AttributesList()

    def tearDown(self):
        """Tear down test fixtures, if any."""
        self._attrs = None

    def test_000_something(self):
        """Test something."""
        pass
