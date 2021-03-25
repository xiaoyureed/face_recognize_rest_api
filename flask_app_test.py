import unittest
import flask_app


class FlaskAppTest(unittest.TestCase):
    def test_show_dataset(self):
        dataset = flask_app.show_dataset()
        print(dataset)


if __name__ == '__main__':
    unittest.main()
