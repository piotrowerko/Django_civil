import math
import numpy as np

from . creep_shrink import CreepShrink
from . axial_and_bend_general import GeneralAxBend


class LongTermLoses():
    """computations of creep of concrete and steel relaxation
    influence on prestressing forces"""
    
    def __init__(self, ro_1000=2.5, ni=0.65, 
                 e_p=195, sigm_c_qp=10):
        self.ro_1000 = ro_1000  # 
        self.ni = ni  # stresses in strands after immediate losses / characteristic strength of steel of the tendons strands
        self.e_p = e_p
        self.sigm_c_qp = sigm_c_qp  # stresses in concrete caused by post-tensioning and and quasi permanent loads on the level of tendons centroid
    
    @staticmethod
    def _sum_of_kwargs_vals(**kwargs):
        pp = [val for val in kwargs.values()]
        return sum(pp)
    
    def relax_loss(self, t):
        delta_sigma_pr = self.ni * GeneralAxBend.R_K_TENDONS \
            * 0.66 * self.ro_1000 * math.e ** (9.1 * self.ni) \
                * (t / 1000) ** (0.75 * (1 - self.ni)) * 10 ** -5
        return delta_sigma_pr
    
    def total_rheo_losses(self, 
                          c_s_member, 
                          pt_cross_sect, 
                          t, 
                          fi_t_t0):
        """returns total rheological losses"""
        delta_sigma_pr = self.relax_loss(t)
        eps_cs = c_s_member.eps_cs_t(t)
        e_cm = c_s_member.e_cm # Young modulus of elasticity of concrete
        ex = pt_cross_sect.e_vert  # vertical position of center of gravity of concrete cross section
        area = pt_cross_sect.area  # area of concrete cross section
        i_cs = pt_cross_sect.i_cs  # axial moment of interia of pt concrete cross section
        t_rel_heights, tend_areas, no_of_layers = pt_cross_sect._tendon_geom()
        t_area = sum(tend_areas)
        z_s = np.abs(np.mean(t_rel_heights))
        nominator = eps_cs * self.e_p + 0.8 * delta_sigma_pr\
            + (self.e_p / e_cm) * fi_t_t0 * self.sigm_c_qp
        denominator = 1 + (self.e_p * t_area) / (e_cm * area) \
            * (1 + (area / i_cs) * z_s ** 2) * (1 + 0.8 * fi_t_t0)
        sigma_c_s_r = nominator / denominator
        return sigma_c_s_r
        
    
def main():
    #print(LongTermLoses._sum_of_kwargs_vals(a=1, b=1, c=100))
    c_s_member = CreepShrink(name='my_member1', cl_conc='C30_37', 
                             ac=1, u=2, 
                             t0=7, temp=20, rh=70,
                             cement_class='N', ts=7)
    my_pt_cross_sec = GeneralAxBend(name='GENERAL_CROSS-SECT_no3b',
                            b=(3, 1.2, 3), # [m] width of the individual rectangles
                            h=(0.25, 1.20, 0.25), # [m] height of the individual rectangles
                            #hsl=0.20, #[m] thickness of upper slab
                            #beff=1.2, #[m] effective width of upper slab
                            cl_conc='C30_37',
                            cl_steel='B500SP',
                            c=25, # [mm]
                            fi=25, # [mm]
                            fi_s=12, # [mm]
                            fi_opp=25, # [mm]
                            nl_reinf_top=(1, (20, 0, 0)), # [mm] denotes number of layers of top reinforcement and corresponding numbers of rebars
                            nl_reinf_bottom=(1, (10, 0 , 0)), # [mm] denotes number of layers of bottom reinforcement and corresponding numbers of rebars
                            m_sd=-4, # [MNm]
                            n_sd=-2, # [MN]
                            tendon_info=(1, (0.200, 3, 20, 150)),
                            prestr_ef_in_mn=False) # [MN]
    my_member = LongTermLoses(ro_1000=2.5, ni=0.65, 
                              e_p=195, sigm_c_qp=6.80)
    alphas = c_s_member._alphas(c_s_member.fcm)
    t0r = c_s_member._t0r(cement_class=c_s_member.cement_class)
    fi_t_t0 = c_s_member.fi_t_t0(100 * 365, alphas, t0r)
    print(my_member.relax_loss(t=500000))
    print(c_s_member)
    print(my_member.total_rheo_losses(c_s_member = c_s_member,
                                      pt_cross_sect=my_pt_cross_sec,
                                      fi_t_t0=fi_t_t0,
                                      t = 500000))
    
if __name__ == '__main__':
    main()