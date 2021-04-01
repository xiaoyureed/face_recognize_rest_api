import unittest
import flask_app


class FlaskAppTest(unittest.TestCase):

    def test_sort_dict(self):
        dic = {'a': 31, 'bc': 5, 'c': 3, 'asd': 4, 'aa': 74, 'd': 0}
        sort_dict = flask_app.sort_dict(dic)
        print(sort_dict)


if __name__ == '__main__':
    unittest.main()
