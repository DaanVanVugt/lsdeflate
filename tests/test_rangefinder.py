#!/usr/bin/env python
import unittest
from context import lsdeflate

class RangeCases(unittest.TestCase):
  """Class containing a set of cases for the rangefinder"""
  # Formatted as a list of tuples min, max, step (inclusive!)
  # for python range function we need to go until step+1
  cases = ([],# empty
           [(1,1,1)],# only [1]
           [(1,2,1)],# [1 2]
           [(1,3,2)],
           [(2,4,1)],
           [(1,1,1),(2,6,2)],
           [(1,2,1),(4,5,1),(8,9,1)],
           [(1,8,1),(10,12,1),(14,16,1)],
           )

  def test_list_to_ranges(self):
    """list_to_ranges of the ranges in self.cases should return those ranges"""
    for case in self.cases:
      lst = sorted(sum(
          map(lambda c: list(range(c[0],c[1]+1,c[2])), case), []))
      # sum concatenates lists (because + operator does that)
      result = lsdeflate.list_to_ranges(lst)
      self.assertEqual(case, result, "list="+repr(lst))

if __name__ == '__main__':
  unittest.main()
