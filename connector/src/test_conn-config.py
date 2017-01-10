from connector import ConnConfig

import unittest

class TestConnConfig(unittest.TestCase):
    """TestCases for connector.ConnConfig"""

    def setUp(self):
        """Set up the default setup"""
        self.default = ConnConfig.DEFAULT_CONFIG
        # TODO Should perform deep copy of dict, in case ConnConfig would
        #      change it during __init__.
        self.config = ConnConfig()

    def testDefaultSuccess(self):
        """Test if default values are properly returned"""
        dc = self.default
        cc = self.config

        self.assertEqual(dc['mappings'], cc.mappings)
        self.assertEqual(dc['listen']['address'], cc.listen.address)
        self.assertEqual(dc['listen']['port'], cc.listen.port)
        self.assertEqual(dc['send']['address'], cc.send.address)
        self.assertEqual(dc['send']['port'], cc.send.port)
        self.assertEqual(dc['broker']['topic'], cc.broker.topic)
        self.assertEqual(dc['broker']['endpoint'], cc.broker.endpoint)
        self.assertEqual(dc['connectorId'], cc.connectorId)

    def testSuccessUpdate(self):
        """Update Success

        Test if default values still work if some are replaced.
        Also if replacing values works.
        """
        dc = self.default
        cc = self.config
        cc.update({'mappings': 'dionaea',
                   'listen': {'port': 0, 'address': 'test'}})

        self.assertEqual('dionaea', cc.mappings)
        self.assertEqual('test', cc.listen.address)
        self.assertEqual(0, cc.listen.port)
        self.assertEqual(dc['send']['address'], cc.send.address)
        self.assertEqual(dc['send']['port'], cc.send.port)
        self.assertEqual(dc['broker']['topic'], cc.broker.topic)
        self.assertEqual(dc['broker']['endpoint'], cc.broker.endpoint)
        self.assertEqual(dc['connectorId'], cc.connectorId)

    def testSuccessInitUpdate(self):
        """Initialization Update Success

        Test if default values still work if some are
        replaced at the initialization
        """
        dc = self.default
        cc = ConnConfig({'mappings': 'dionaea', 'listen': {'port': 7080,
                                                           'address': 'test'}})

        self.assertEqual('dionaea', cc.mappings)
        self.assertEqual('test', cc.listen.address)
        self.assertEqual(7080, cc.listen.port)
        self.assertEqual(dc['send']['address'], cc.send.address)
        self.assertEqual(dc['send']['port'], cc.send.port)
        self.assertEqual(dc['broker']['topic'], cc.broker.topic)
        self.assertEqual(dc['broker']['endpoint'], cc.broker.endpoint)
        self.assertEqual(dc['connectorId'], cc.connectorId)

    def testSuccessMissingValue(self):
        """Missing Value Success

        Test value must not be missing after a nested key
        is only partially replaced
        """
        dc = self.default
        cc = ConnConfig({'listen': {'port': 7080}})

        # the essential check:
        self.assertTrue('address' in cc.listen)
        self.assertEqual(dc['listen']['address'], cc.listen.address)
        self.assertEqual(7080, cc.listen.port)

        # testing unrelated defaults:
        self.assertEqual(dc['send']['address'], cc.send.address)
        self.assertEqual(dc['mappings'], cc.mappings)
        # We already have tests for the general behaviour of ConnConfig. We do
        # not need to test everything everytime.

    def testFailureInvalidKey(self):
        """Invalid Key Failure

        Test exception being thrown when a key for
        updating the config is invalid (should not exist)
        """
        self.assertRaises(KeyError, self.config.update,
                          {'mappings': 'dionaea', 'address': 5000,
                           'listennnnn': {'port': 8080}})

if __name__ == '__main__':
    unittest.main()
