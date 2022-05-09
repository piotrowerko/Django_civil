import math



# if __name__ == '__main__':
#     from rect_single_reinf import RectCrSectSingle
# else:
#     from . rect_single_reinf import RectCrSectSingle

from . rect_single_reinf import RectCrSectSingle


class RectCrSectDoubleR(RectCrSectSingle):
    """bending of rectangular cross section with double reinforcement:
    evaluation of bending moment capasity [kNm];
    Lapko Jensen fig. 4.17b"""
    def __init__(self, name, b, h, cl_conc, cl_steel, 
                 c, fi, fi_s, 
                 fi_opp, no_of_bars=2, no_of_opp_bars=2):
        super().__init__(name, b, h, 
                         cl_conc, cl_steel, c, 
                         fi, fi_s, no_of_bars)
        self.fi_opp = fi_opp  # diameter of second package of reinforcement
        self.no_of_opp_bars = no_of_opp_bars

    def _compute_a2(self):
        """returns a2 value assuming one row of reinf"""
        return (self.c + 0.5 * self.fi_opp + self.fi_s) / 1000

    def _compute_a_s2(self):
        """return an area of e.g. upper reinforcement"""
        # num_of_reb = float(input('input num of upper rebars: ').strip())  #.split()
        num_of_reb = self.no_of_opp_bars
        return math.pi * (self.fi_opp / 1000) ** 2 / 4 * num_of_reb

    def _compute_ksi_eff_double_r(self):
        a_s1 = self._compute_a_s1()
        a_s2 = self._compute_a_s2()
        f_yd = self.cl_steel_data[1]
        f_cd = self._get_fcd_eta()
        nominator = a_s1 * f_yd - a_s2 * f_yd
        denominator = self.b * self._compute_d() * f_cd
        ksi_eff = nominator / denominator
        x_eff = ksi_eff * self._compute_d()
        return ksi_eff, a_s1, a_s2, x_eff

    def compute_m_rd_double_r(self):
        ksi_eff, a_s1, a_s2, x_eff = self._compute_ksi_eff_double_r()
        d = self._compute_d()
        f_cd = self._get_fcd_eta()
        a2 = self._compute_a2()
        if ksi_eff <= self.cl_steel_data[3]:
            print("reinforcement is fully used; sigma_s = f_yd")
            if ksi_eff > 2 * a2 / d:
                print("ksi_eff > 2 * a2 / d")
                m_rd = 1000 * ksi_eff * (1 - 0.5 * ksi_eff) * d ** 2 * self.b * f_cd \
                + 1000 * (a_s2 * (d - a2) * self.cl_steel_data[1])
                return round(m_rd, 2), round(ksi_eff, 4), round(x_eff, 4)
            else:
                print("ksi_eff <= 2 * a2 / d")
                m_rd = 1000 * a_s1 * (d - a2) * self.cl_steel_data[1]
                return round(m_rd, 2), round(ksi_eff, 4), round(x_eff, 4)
        else:
            print("reinforcement is NOT fully used; sigma_s < f_yd")
            ksi_eff = self.cl_steel_data[3]  # # ksi_eff_lim assuming LAMBDA = 0.8 and EPSILON CU = 3.5 * (10 ** -3)
            m_rd = 1000 * ksi_eff * (1 - 0.5 * ksi_eff) * d ** 2 * self.b * f_cd
            return round(m_rd, 2), round(ksi_eff, 4), round(x_eff, 4)

def main():
    my_double_reinf_cross_sec = RectCrSectDoubleR(name='moj_przekr_prost',
                                                  b=0.7,
                                                  h=1.2,
                                                  cl_conc='C30_37',
                                                  cl_steel='B500SP',
                                                  c=40,
                                                  fi=32,
                                                  no_of_bars=7,
                                                  fi_s=10,
                                                  fi_opp=16,
                                                  no_of_opp_bars=4)
    results = my_double_reinf_cross_sec.compute_m_rd_double_r()
    print(f'ksi eff:  {results[1]}')
    print(f'x_eff:  {results[2]}')
    print(f'max. load capasity bending moment:  {results[0]}')

if __name__ == '__main__':
    main()
