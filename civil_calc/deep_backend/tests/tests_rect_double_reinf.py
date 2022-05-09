import unittest
from .. rect_double_reinf import RectCrSectDoubleR

class TesRectCrSectDoubleR(unittest.TestCase):

    def test_reinforcement_fully_used_first(self):
        """Test case when reinforcement is fully used and ksi_eff > 2 * a2 / d"""
        cross_section = RectCrSectDoubleR('rectangular', 0.7, 1.2, 'C30_37', 'B500SP', 40, 32, 10, 16, 7, 4)
        self.assertEqual(cross_section.compute_m_rd_double_r(), (2609.94, 0.1234, 0.1399))

    def test_reinforcement_fully_used_secend(self):
        """Test case when reinforcement is fully used and ksi_eff > 2 * a2 / d"""
        cross_section = RectCrSectDoubleR('rectangular', 0.45, 0.7, 'C25_30', 'BSt500S', 40, 25, 10, 12, 6, 2)
        self.assertEqual(cross_section.compute_m_rd_double_r(), (724.21, 0.2309, 0.1472))

    def test_reinforcement_fully_used_third(self):
        """Test case when reinforcement is fully used and ksi_eff <= 2 * a2 / d"""
        cross_section = RectCrSectDoubleR('rectangular', 0.7, 1.0, 'C25_30', 'BSt500S', 30, 25, 8, 12, 6, 6)
        self.assertEqual(cross_section.compute_m_rd_double_r(), (1160.11, 0.0831, 0.0789))

    def test_reinforcement_fully_used_fourth(self):
        """Test case when reinforcement is fully used and ksi_eff <= 2 * a2 / d"""
        cross_section = RectCrSectDoubleR('rectangular', 0.35, 0.8, 'C35_45', 'B500SP', 40, 20, 10, 12, 8, 4)
        self.assertEqual(cross_section.compute_m_rd_double_r(), (747.80, 0.1385, 0.1025))

    def test_reinforcement_not_fully_used_first(self):
        """Test case when reinforcement is not fully used"""
        cross_section = RectCrSectDoubleR('rectangular', 0.55, 0.8, 'C20_25', 'B500SP', 30, 32, 6, 12, 9, 2)
        self.assertEqual(cross_section.compute_m_rd_double_r(), (1649.03, 0.5, 0.3881))

    def test_reinforcement_not_fully_used_second(self):
        """Test case when reinforcement is not fully used"""
        cross_section = RectCrSectDoubleR('rectangular', 0.5, 0.7, 'C20_25', 'BSt500S', 40, 32, 10, 12, 7, 2)
        self.assertEqual(cross_section.compute_m_rd_double_r(), (1076.99, 0.5, 0.329))

if __name__ == '__main__':
    unittest.main()