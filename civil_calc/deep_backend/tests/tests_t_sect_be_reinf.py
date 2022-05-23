import unittest
from .. t_sect_ben_reinf import TCrReinf

class TestTCrRein(unittest.TestCase):
    
    def test_find_reinf_first(self):
        """Test casse when compression zone does not extends below the plate"""
        cross_section = TCrReinf('t-shape', 0.4, 0.45, 'C20_25', 'BSt500S', 
                                 35, 16, 10, 10, 200, 0.1, 0.75)
        result = cross_section.compute_reinf_T()
        self.assertAlmostEqual(result[0][0], 0.0012362)
        self.assertEqual(result[0][1], 7)
        self.assertAlmostEqual(result[0][2], 0)
        self.assertEqual(result[0][3], 0)
        self.assertEqual(result[1], 'The compression zone does NOT extends below the plate')

    def test_find_reinf_second(self):
        """Test casse when compression zone does not extends below the plate"""
        cross_section = TCrReinf('t-shape', 0.6, 1.0, 'C30_37', 'B500SP', 
                                 30, 32, 10, 116, 2500, 0.15, 0.9)
        result = cross_section.compute_reinf_T()
        self.assertAlmostEqual(result[0][0], 0.0066100)
        self.assertEqual(result[0][1], 9)
        self.assertAlmostEqual(result[0][2], 0)
        self.assertEqual(result[0][3], 0)
        self.assertEqual(result[1], 'The compression zone does NOT extends below the plate')

    def test_find_reinf_third(self):
        """Test case when compression zone extends below the plate and only
        the As1 reinforcement is sufficient"""
        cross_section = TCrReinf('t-shape', 0.4, 0.45, 'C20_25', 'BSt500S', 
                                 35, 25, 10, 10, 400, 0.1, 0.75)
        result = cross_section.compute_reinf_T()
        self.assertAlmostEqual(result[0][0], 0.0027319)
        self.assertEqual(result[0][1], 6)
        self.assertAlmostEqual(result[0][2], 0)
        self.assertEqual(result[0][3], 0)
        self.assertEqual(result[1], 'only the As1 reinforcement is sufficient')

    def test_find_reinf_fourth(self):
        """Test case when compression zone extends below the plate and only
        the As1 reinforcement is sufficient"""
        cross_section = TCrReinf('t-shape', 0.5, 0.85, 'C25_30', 'B500SP', 
                                 30, 25, 10, 16, 1500, 0.1, 0.9)
        result = cross_section.compute_reinf_T()
        self.assertAlmostEqual(result[0][0], 0.0047152)
        self.assertEqual(result[0][1], 10)
        self.assertAlmostEqual(result[0][2], 0)
        self.assertEqual(result[0][3], 0)
        self.assertEqual(result[1], 'only the As1 reinforcement is sufficient')

    def test_find_reinf_fifth(self):
        """Test case when compression zone extends below the plate and 
        As2 reinforcement is necessary"""
        cross_section = TCrReinf('t-shape', 0.4, 0.45, 'C20_25', 'BSt500S', 
                                 35, 32, 10, 10, 540, 0.1, 0.75)
        result = cross_section.compute_reinf_T()
        self.assertAlmostEqual(result[0][0], 0.0040181)
        self.assertEqual(result[0][1], 5)
        self.assertAlmostEqual(result[0][2], 0.0003126)
        self.assertEqual(result[0][3], 4)
        self.assertEqual(result[1], 'As2 reinforcement is necessary')

    def test_find_reinf_sixth(self):
        """Test case when compression zone extends below the plate and 
        As2 reinforcement is necessary"""
        cross_section = TCrReinf('t-shape', 0.5, 0.6, 'C25_30', 'B500SP', 
                                 30, 32, 10, 12, 1500, 0.1, 0.80)
        result = cross_section.compute_reinf_T()
        self.assertAlmostEqual(result[0][0], 0.0079433)
        self.assertEqual(result[0][1], 10)
        self.assertAlmostEqual(result[0][2], 0.0011277)
        self.assertEqual(result[0][3], 10)
        self.assertEqual(result[1], 'As2 reinforcement is necessary')


    def test_find_reinf_seventh(self):
        """Test case when data input is wrong"""
        cross_section = TCrReinf('t-shape', 0.4, 0.45, 'C20_25', 'BSt500S', 
                                 35, 32, 10, 10, 700, 0.1, 0.75)
        result = cross_section.compute_reinf_T()
        self.assertAlmostEqual(result[0][0], 0)
        self.assertEqual(result[0][1], 0)
        self.assertAlmostEqual(result[0][2], 0)
        self.assertEqual(result[0][3], 0)
        self.assertEqual(result[1], 'WARNING: complex roots of equation system - try diff. input')

if __name__ == '__main__':
    unittest.main()