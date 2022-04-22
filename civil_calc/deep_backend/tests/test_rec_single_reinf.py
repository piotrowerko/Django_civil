import unittest
from .. rect_single_reinf import RectCrSectSingle

class TestRectCrSectSingle(unittest.TestCase):
    
    def test_reinforcement_fully_used_first(self):
        """Test case when reinforcement is fully used"""
        cross_section = RectCrSectSingle('rectangular', 0.5, 1.0, 'C30_37', 'B500SP', 40, 25, 12, 5)
        self.assertEqual(cross_section.compute_m_rd_single_r(), (945.60, 0.1065, 0.0996))
    
    def test_reinforcement_fully_used_second(self):
        """Test case when reinforcement is fully used"""
        cross_section = RectCrSectSingle('rectangular', 0.6, 1.4, 'C40_50', 'BSt500S', 35, 32, 10, 8)
        self.assertEqual(cross_section.compute_m_rd_single_r(), (3519.09, 0.1219, 0.1633))

    def test_reinforcement_not_fully_used_first(self):
        """Test case when reinforcement is not fully used"""
        cross_section = (RectCrSectSingle('rectangular', 0.3, 0.5, 'C20_25', 'BSt500S', 30, 20, 8, 8))
        self.assertEqual(cross_section.compute_m_rd_single_r(), (328.44, 0.5, 0.255))

    def test_reinforcement_not_fully_used_second(self):
        """Test case when reinforcement is not fully used"""
        cross_section = (RectCrSectSingle('Rectangular', 0.25, 0.40, 'C16_20', 'B500SP', 30, 16, 8, 6))
        self.assertEqual(cross_section.compute_m_rd_single_r(), (134.28, 0.5, 0.1836))

if __name__ == '__main__':
    unittest.main()