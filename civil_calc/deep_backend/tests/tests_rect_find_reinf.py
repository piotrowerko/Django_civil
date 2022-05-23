import unittest
from .. rect_find_reinf import RectCrReinf

class TestRectCrReinf(unittest.TestCase):
    
    def test_find_reinf_first(self):
        """Test case when only the As1 reinforcement is sufficient"""
        cross_section = RectCrReinf('rectangular', 0.5, 0.8, 'C30_37', 'BSt500S', 
                                    30, 32, 12, 16, 1000)
        result = cross_section.compute_reinf_rect()
        self.assertAlmostEqual(result[0], 0.0034177)
        self.assertEqual(result[1], 5)
        self.assertAlmostEqual(result[2], 0)
        self.assertEqual(result[3], 0)
        self.assertEqual(result[4], 'only the As1 reinforcement is sufficient')

    def test_find_reinf_second(self):
        """Test case when only the As1 reinforcement is sufficient"""
        cross_section = RectCrReinf('rectangular', 0.45, 0.9, 'C20_25', 'B500SP', 
                                    30, 25, 10, 12, 1200)
        result = cross_section.compute_reinf_rect()
        self.assertAlmostEqual(result[0], 0.003845044)
        self.assertEqual(result[1], 8)
        self.assertAlmostEqual(result[2], 0)
        self.assertEqual(result[3], 0)
        self.assertEqual(result[4], 'only the As1 reinforcement is sufficient')

    def test_find_reinf_third(self):
        """Test case when As2 reinforcement is necessary"""
        cross_section = RectCrReinf('rectangular', 0.6, 1.0, 'C25_30', 'B500SP', 
                                    40, 32, 10, 16, 3700)
        result = cross_section.compute_reinf_rect()
        self.assertAlmostEqual(result[0], 0.012014558)
        self.assertEqual(result[1], 15)
        self.assertAlmostEqual(result[2], 0.000510254)
        self.assertEqual(result[3], 3)
        self.assertEqual(result[4], 'As2 reinforcement is necessary')

    def test_find_reinf_fourth(self):
        """Test case when As2 reinforcement is necessary"""
        cross_section = RectCrReinf('rectangular', 0.3, 0.5, 'C25_30', 'BSt500S', 
                                    30, 32, 8, 12, 500)
        result = cross_section.compute_reinf_rect()
        self.assertAlmostEqual(result[0], 0.003320474)
        self.assertEqual(result[1], 5)
        self.assertAlmostEqual(result[2], 0.000573729)
        self.assertEqual(result[3], 6)
        self.assertEqual(result[4], 'As2 reinforcement is necessary')

    def test_find_reinf_fifth(self):
        """Test case when data input is wrong"""
        cross_section = RectCrReinf('rectangular', 0.5, 0.8, 'C30_37', 'BSt500S', 
                                    30, 32, 12, 16, 3000)
        result = cross_section.compute_reinf_rect()
        self.assertAlmostEqual(result[0], 0)
        self.assertEqual(result[1], 0)
        self.assertAlmostEqual(result[2], 0)
        self.assertEqual(result[3], 0)
        self.assertEqual(result[4], 'WARNING: complex roots of equation system - try diff. input')
        
if __name__ == '__main__':
    unittest.main()