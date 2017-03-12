from django.test import TestCase


class GenericTestCase(TestCase):

    def test_bla(self):
        print('testing bla')
        self.assertEquals(1, 1)