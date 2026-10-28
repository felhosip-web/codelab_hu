# -*- coding: utf-8 -*-
import unittest
from core.plugin_system import PluginLoader
from core.step import VisualizationStep


class TestMathNumericalAlgorithms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = PluginLoader()
        cls.loader.load_all()

    def test_factorial_contract(self):
        """
        Tests factorial plugin for n=1 (1) and n=5 (120).
        """
        plugin = self.loader.get_plugin("factorial")
        self.assertIsNotNone(plugin)

        plugin.set_param("n", 1)
        steps1 = list(plugin.get_steps([]))
        self.assertEqual(steps1[-1].extra["result"], 1)

        plugin.set_param("n", 5)
        steps = list(plugin.get_steps([]))
        self.assertGreater(len(steps), 0)

        for step in steps:
            self.assertIsInstance(step, VisualizationStep)

        final_step = steps[-1]
        self.assertEqual(final_step.extra["result"], 120)

    def test_fibonacci_contract(self):
        """
        Tests fibonacci_iter plugin: F(3) = 2, F(8) = 21.
        """
        plugin = self.loader.get_plugin("fibonacci_iter")
        self.assertIsNotNone(plugin)

        plugin.set_param("n", 3)
        steps3 = list(plugin.get_steps([]))
        self.assertEqual(steps3[-1].extra["result"], 2)

        plugin.set_param("n", 8)
        steps = list(plugin.get_steps([]))
        self.assertGreater(len(steps), 0)

        final_step = steps[-1]
        self.assertEqual(final_step.extra["result"], 21)

    def test_gcd_contract(self):
        """
        Tests LNKO - Euklideszi plugin: gcd(48, 18) = 6, gcd(17, 13) = 1.
        """
        plugin = self.loader.get_plugin("gcd")
        self.assertIsNotNone(plugin)

        plugin.set_param("a", 17)
        plugin.set_param("b", 13)
        steps1 = list(plugin.get_steps([]))
        self.assertEqual(steps1[-1].extra["result"], 1)

        plugin.set_param("a", 48)
        plugin.set_param("b", 18)
        steps = list(plugin.get_steps([]))
        self.assertGreater(len(steps), 0)

        final_step = steps[-1]
        self.assertEqual(final_step.extra["result"], 6)

    def test_hanoi_contract(self):
        """
        Tests Hanoi tornyai plugin for n=3 disks -> 7 moves, n=4 disks -> 15 moves.
        """
        plugin = self.loader.get_plugin("hanoi")
        self.assertIsNotNone(plugin)

        plugin.set_param("n", 3)
        steps = list(plugin.get_steps([]))
        self.assertEqual(steps[-1].extra["total"], 7)

        plugin.set_param("n", 4)
        steps4 = list(plugin.get_steps([]))
        self.assertEqual(steps4[-1].extra["total"], 15)

    def test_sieve_contract(self):
        """
        Tests Prímszita - Eratoszthenész plugin for n=30 -> 10 primes.
        """
        plugin = self.loader.get_plugin("sieve")
        self.assertIsNotNone(plugin)

        plugin.set_param("n", 30)
        steps = list(plugin.get_steps([]))
        self.assertGreater(len(steps), 0)

        final_step = steps[-1]
        expected_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        self.assertEqual(final_step.extra["primes"], expected_primes)

    def test_power_contract(self):
        """
        Tests Hatvány plugin for 2^10 = 1024, 3^4 = 81.
        """
        plugin = self.loader.get_plugin("power")
        self.assertIsNotNone(plugin)

        plugin.set_param("base", 3)
        plugin.set_param("exp", 4)
        steps3 = list(plugin.get_steps([]))
        self.assertEqual(steps3[-1].extra["result"], 81)

        plugin.set_param("base", 2)
        plugin.set_param("exp", 10)
        steps = list(plugin.get_steps([]))
        self.assertGreater(len(steps), 0)

        final_step = steps[-1]
        self.assertEqual(final_step.extra["result"], 1024)

    def test_prime_factor_contract(self):
        """
        Tests Prímtényezős felbontás plugin for 60 -> [2, 2, 3, 5].
        """
        plugin = self.loader.get_plugin("prime_factor")
        self.assertIsNotNone(plugin)

        plugin.set_param("n", 60)
        steps = list(plugin.get_steps([]))
        self.assertGreater(len(steps), 0)

        final_step = steps[-1]
        self.assertEqual(final_step.extra["factors"], [2, 2, 3, 5])

    def test_palindrome_contract(self):
        """
        Tests Palindrom plugin for "racecar" (True) and "hello" (False).
        """
        plugin = self.loader.get_plugin("palindrome")
        self.assertIsNotNone(plugin)

        plugin.set_param("word", "racecar")
        steps = list(plugin.get_steps([]))
        self.assertTrue(steps[-1].extra["is_palindrome"])

        plugin.set_param("word", "hello")
        steps2 = list(plugin.get_steps([]))
        self.assertFalse(steps2[-1].extra["is_palindrome"])


if __name__ == "__main__":
    unittest.main()
