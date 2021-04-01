import unittest

from util.str_utils import gen_uuid


class StrUtilsTest(unittest.TestCase):

    def test_gen_uuid(self):
        uuid = gen_uuid("hello")
        print(uuid)
