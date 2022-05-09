"""
sources of knoweladge
knauf
łapko jensen
pietryga
https://chodor-projekt.net/encyclopedia/krzywe-interakcji-m-n-zelbetu/
oleszek
"""

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

from . t_sect_ben_reinf import TCrReinf
from . char_geom import CharGeom

class GeneralAxBend(TCrReinf):
    """cross section axial force + bending moment capasity computations;
    returns stresses in conrete and steel layers according to computed itaratively
    (gradient descent) epsilon and fi (strain and rotation of cross section) 
    to achive close resulting M and N as M_sd and N_sd
    [compression is denoted by plus sign]"""
    EC2 = 0.0020  # concrete strain of section in the begining of flat (plastic) stresses
    ECU2 = 0.0035  # max. concrete strain of section
    EYD = 0.00217  # steel strain in Hook's region (FOR BOTH B500SP AND BST500S STEEL)
    _R = 20  # curve parameter (FOR BOTH B500SP AND BST500S STEEL ?)
    E_STELL = 200 * 10 ** 3  # acc. to [2]
    E_TENDONS = 195 * 10 ** 3
    E_EK_TENDONS = 0.010  # max. strain in the steel of the tendons
    R_K_TENDONS = 1860  # [MPa] characteristic strength of steel of the tendons
    EPS_INIT = 0.001 * 10 ** -2
    EPS_T_INIT = - 0.70 * R_K_TENDONS / E_TENDONS  # inital linear strain in tednon due to inital stressing force (uwględniono straty trwałe? lub nie)
    N_CONC_LAYERS = 30  # number of layers of virtual division of the concrete cross-section for the needs of numerical integrals
    CONC_L_THIC = 0.005 # concrete layer thickness of virtual division of the concrete cross-section for the needs of numerical integrals
    ETA = 0.9 # learning rate

    def __init__(self, name, b, h, 
                 cl_conc, cl_steel, 
                 c, fi, fi_s, fi_opp, 
                 nl_reinf_top, nl_reinf_bottom,
                 m_sd, n_sd, tendon_info=None, 
                 prestr_ef_in_mn=True):  # efekt sprężenia obecny w podanej przez użytkownika parze MN
        super().__init__(name, b, h, cl_conc, cl_steel, c,
                        fi, fi_s, fi_opp, m_sd)
        self.n_sd = n_sd
        char_geom = CharGeom()
        #self.e_vert = char_geom.find_center_m((b[2], h[2], b[1], h[1], b[0], h[0]))[0]  # = sefl.h_bottom
        self.e_vert = char_geom.find_center_m((b[0], h[0], b[1], h[1], b[2], h[2]))[0]  # = sefl.h_bottom
        self.h_top = sum(self.h) - self.e_vert
        self.nl_reinf_top = nl_reinf_top
        self.nl_reinf_bottom = nl_reinf_bottom
        self.fi_init = GeneralAxBend.EPS_INIT / max(self.e_vert, self.h_top)
        self.tendon_info = tendon_info
        self.prestr_ef_in_mn = prestr_ef_in_mn

    @classmethod
    def alter_constr(self):
        """alternative contructor with custom reinforcement heights"""
        pass
    
    @staticmethod
    def trial_plot(input_list, second_input_list=None, title=None):
        if second_input_list==None:
            fig0, ax0 = plt.subplots()
            plt.barh(input_list, [i for i in range(len(input_list))], height=0.01)
        else:
            plt.barh(input_list, second_input_list, height=0.01)
        plt.title(title)
        plt.grid(True)
        plt.show()

    @staticmethod
    def _solve_two_eq(np_l_array, np_r_array):
        """returns new value of eps and fi cur
        by solving linear system of two equations with two variables"""
        return np.linalg.solve(np_l_array, np_r_array)

    @property
    def E_cm(self):
        """returns E_cm value according to EC"""
        conc_data = self._load_concrete(file_path='concrete_ec.csv')
        conc_class_names = [el[0] for el in conc_data]
        class_ind = conc_class_names.index(self.cl_conc)
        self._E_cm = float(conc_data[class_ind][9])
        return self._E_cm  # kluczowe pytanie - czym się różni atrybut od właściwości klasy (odp: wła. ma setter i deleter)

    # def _initial_rotation(self):
    #     # ROTACJA TAKA ŻEBY DAŁA JEDNĄ SETNĄ PROMILA W SKRAJNYCH WŁÓKNACH
    #     fi_init = GeneralAxBend.EPS_INIT / max(self.e_vert, self.h_top)
    #     return fi_init

    def _conc_layers(self):
        """finds heights and number of layers of virtual division in the concrete cross-section"""
        n_layers = int(sum(self.h) / GeneralAxBend.CONC_L_THIC)
        conc_lay_heights = []
        conc_lay_widths = []
        conc_lay_areas = []
        for i in range(n_layers):
            curr_rel_height = self.h_top - (0.5 + i) * GeneralAxBend.CONC_L_THIC
            curr_height = sum(self.h) - (0.5 + i) * GeneralAxBend.CONC_L_THIC
            conc_lay_heights.append(curr_rel_height)
            if curr_height < self.h[0]:
                conc_lay_widths.append(self.b[0])
            elif curr_height > self.h[0] and curr_height < (self.h[0]+self.h[1]):
                conc_lay_widths.append(self.b[1])
            else:
                conc_lay_widths.append(self.b[2])
            conc_lay_areas.append(GeneralAxBend.CONC_L_THIC * conc_lay_widths[i])
        return n_layers, conc_lay_heights, conc_lay_widths, conc_lay_areas

    def _strains_in_conc(self, eps_cur=0.0, fi_cur=0.0, conc_geom=None):
        """finds strain in concrete layers basing on rotation and eps_linear"""
        n_layers, conc_lay_heights, conc_lay_widths, conc_lay_areas = conc_geom
        strain_conc = [(conc_lay_heights[i] * fi_cur + eps_cur) for i in range(n_layers)]
        return strain_conc, n_layers, conc_lay_heights, conc_lay_widths, conc_lay_areas

    def _stress_strain_conc(self, strain_conc=0.0):
        """returns stress-strain relationsip in cocnrete"""
        f_cd = self._get_fcd_eta()
        if strain_conc >= GeneralAxBend.EC2 and strain_conc <= GeneralAxBend.ECU2:
            sigma_conc = 6.67 * strain_conc + f_cd - 0.0133
        elif strain_conc < GeneralAxBend.EC2 and strain_conc >= 0:
            sigma_conc = f_cd * (1 - (1 - strain_conc / GeneralAxBend.EC2) ** 2)
        elif strain_conc < 0:
            sigma_conc = 0
        else:  # strain_conc > GeneralAxBend.ECU2
            sigma_conc = strain_conc * (f_cd / GeneralAxBend.ECU2)
        return sigma_conc

    def _stress_in_conc(self, eps_cur=0.0, fi_cur=0.0, conc_geom=None):
        """returns stresses in concrete layers"""
        strain_conc, n_layers, conc_lay_heights, conc_lay_widths, conc_lay_areas = self._strains_in_conc(eps_cur, fi_cur, conc_geom)
        stress_conc = [self._stress_strain_conc(el) for el in strain_conc]
        return stress_conc, n_layers, conc_lay_heights, conc_lay_widths, conc_lay_areas, strain_conc

    def _reinf_geom(self):
        """returns reinforcement geometrical deatials"""
        layer_one = self.c + self.fi_s + self.fi * 0.5
        layer_one_opp = self.c + self.fi_s + self.fi_opp * 0.5
        n_bott, rebar_numbers_bott = self.nl_reinf_bottom
        n_upp, rebar_numbers_upp = self.nl_reinf_top
        n_of_layers = n_bott + n_upp
        reinf_heights = [(0.001 * layer_one + 0.002 * i * self.fi) for i in range(n_bott)] \
            + [(sum(self.h) - 0.001 * layer_one_opp - 0.002 * i * self.fi_opp) for i in range(n_upp - 1, -1, -1)]
        r_rel_heights = self._relative_heights(reinf_heights)
        single_bar_area_bot =  math.pi * ((0.001 * self.fi) ** 2) / 4
        single_bar_area_upp =  math.pi * ((0.001 * self.fi_opp) ** 2) / 4
        reinf_areas = [rebar_numbers_bott[i] * single_bar_area_bot for i in range(n_bott)] \
            + [rebar_numbers_upp[i] * single_bar_area_upp for i in range(n_upp)]
        return r_rel_heights, reinf_areas, n_of_layers
    
    def _tendon_geom(self):
        """returns geometrical deatails of tendons"""
        t_inf = self.tendon_info
        tend_heights = []
        tend_areas = []
        no_of_layers = t_inf[0]
        for i, el in enumerate(t_inf, start=0):
            if i > 0:
                tend_heights.append(el[0])
                tend_areas.append(el[1] * el[2] * el[3] * 10 ** - 6)
        t_rel_heights = self._relative_heights(tend_heights)
        return t_rel_heights, tend_areas, no_of_layers
    
    def _strains_in_steel(self, eps_cur=0.0, fi_cur=0.0, reinf_geom=None):
        """finds strain in steel layers basing on rotation and eps_linear"""
        r_heights, reinf_areas, n_of_layers = reinf_geom
        strain_steel = [0] * n_of_layers
        for i in range(n_of_layers):
            strain_steel[i] = (r_heights[i] * fi_cur) + eps_cur
        return strain_steel, r_heights, reinf_areas

    def _strains_in_tendons(self, eps_cur=0.0, fi_cur=0.0, tend_geom=None):
        """finds strain in steel of tendons basing on rotation and eps_linear"""
        # WARNING: INITIAL EPSILON MUST BE COMPUTED!!!
        t_heights, t_areas, n_of_layers = tend_geom
        strain_tendon = [GeneralAxBend.EPS_T_INIT] * n_of_layers
        for i in range(n_of_layers):
            strain_tendon[i] += (t_heights[i] * fi_cur) + eps_cur
        return strain_tendon, t_heights, t_areas

    def _stress_strain_steel(self, strain_steel=0.0):
        """returns stress-strain relationsip in steel"""
        #k = self.cl_steel_data[6]
        e_uk = self.cl_steel_data[5]
        e_ud = e_uk / 1.15
        f_yd = self.cl_steel_data[1]
        #strain_s_dash = strain_steel / GeneralAxBend.EYD
        #sigma_s_dash = k * strain_s_dash + ((1 - k) * strain_s_dash) / ((1 + strain_s_dash ** GeneralAxBend._R) ** (1 / GeneralAxBend._R))
        #sigma_steel = f_yd * sigma_s_dash
        #k_si = k  + (1 - k) / ((1 + strain_s_dash ** GeneralAxBend._R) ** (1 / GeneralAxBend._R))
        if abs(strain_steel) < GeneralAxBend.EYD:
            sigma_steel = GeneralAxBend.E_STELL * strain_steel
        elif abs(strain_steel) >= GeneralAxBend.EYD and abs(strain_steel) <= e_ud:
            a = 1 / (e_ud - GeneralAxBend.EYD)
            b = f_yd - a * GeneralAxBend.EYD
            _sigma = a * abs(strain_steel) + b
            #sigma_steel = math.copysign(f_yd, strain_steel)
            sigma_steel = math.copysign(_sigma, strain_steel)
        else:  # abs(strain_steel) > e_yd
            sigma_steel = strain_steel * (f_yd / e_ud)
        # WARINING: doubling of stresses in the reinforcement surrounded 
        # by concrete in compression was not taken into account!!
        return sigma_steel, e_ud
    
    def _stress_strain_tendons(self, strain_tendon=0.0):
        """returns stress-strain relationsip in in the steel of the tendons"""
        e_uk = GeneralAxBend.E_EK_TENDONS
        e_ud = e_uk / 1.00
        #f_yk = GeneralAxBend.R_K_TENDONS
        E_tendons = GeneralAxBend.E_TENDONS
        sigma_tendon = E_tendons * strain_tendon
        return sigma_tendon, e_ud

    def _stress_in_steel(self, eps_cur=0.0, fi_cur=0.0, reinf_geom=None):
        """returns stresses in reinforcement layers"""
        strain_steel, r_heights, reinf_areas = self._strains_in_steel(eps_cur, fi_cur, reinf_geom)
        stress_steel = [self._stress_strain_steel(el)[0] for el in strain_steel]
        return stress_steel, r_heights, reinf_areas, strain_steel
    
    def _stress_in_tendons(self, eps_cur=0.0, fi_cur=0.0, tend_geom=None):
        """returns stresses in tendons layers"""
        strain_t, t_heights, t_areas = self._strains_in_tendons(eps_cur, fi_cur, tend_geom)
        stress_tend = [self._stress_strain_tendons(el)[0] for el in strain_t]
        return stress_tend, t_heights, t_areas, strain_t
    

    def _relative_heights(self, heights):
        "returns heights relative to center of gravity"
        rel_heights = [(i - self.e_vert) for i in heights]
        return rel_heights

    def _internal_forces(self, eps_cur, fi_cur, conc_geom, reinf_geom, tend_geom):
        """numerical integral for internal axial force and bending moment computation;
        takes given strain and rotation,
        returns corresponding axial force abd bending moment"""
        _a = self._stress_in_conc(eps_cur, fi_cur, conc_geom)
        stress_in_conc, conc_lay_heights, conc_areas, strain_conc = _a[0], _a[2], _a[4], _a[5]
        stress_in_steel, r_heights, steel_areas, strain_steel = self._stress_in_steel(eps_cur, fi_cur, reinf_geom)
        stress_in_t, t_heights, t_areas, strain_t = self._stress_in_tendons(eps_cur, fi_cur, tend_geom)
        # suma pole_plastra*naprezenieplastra
        # suma pole_warw_pretow*naprezenia_w_wawie-pretow
        forces_in_conc = [stress_in_conc[i] * conc_areas[i] \
            for i in range(len(stress_in_conc))]
        forces_in_steel = [stress_in_steel[i] * steel_areas[i] \
            for i in range(len(stress_in_steel))]
        forces_in_t = [stress_in_t[i] * t_areas[i] \
            for i in range(len(stress_in_t))]
        axial_force = sum(forces_in_conc + forces_in_steel + forces_in_t)
        # suma pole_plastra*naprezenieplastra*odlegloscdoSRC
        # suma pole_warw_pretow*naprezenia_w_wawie-pretow*odlegl_doSRC
        bending_moment_conc = [forces_in_conc[i] * conc_lay_heights[i] for i in range(len(forces_in_conc))]
        bending_moment_steel = [forces_in_steel[i] * r_heights[i] for i in range(len(forces_in_steel))]
        bending_moment_tend = [forces_in_t[i] * t_heights[i] for i in range(len(forces_in_t))]
        bending_moment = sum(bending_moment_conc + bending_moment_steel + bending_moment_tend)
        return axial_force, \
                sum(bending_moment_conc), \
                sum(bending_moment_steel), \
                sum(bending_moment_tend), \
                strain_steel, \
                stress_in_steel, \
                forces_in_steel, r_heights, \
                strain_t, \
                stress_in_t, \
                forces_in_t, t_heights, \
                strain_conc, \
                stress_in_conc, \
                forces_in_conc, conc_lay_heights, \
                bending_moment

    def _get_n1_and_m1(self, conc_geom, reinf_geom):
        eps_init = GeneralAxBend.EPS_INIT
        n1_e, m1_e = self._internal_forces(eps_init, 0, conc_geom, reinf_geom)[0], self._internal_forces(eps_init, 0, conc_geom, reinf_geom)[-1]
        fi_init = self._initial_rotation()
        n1_fi, m1_fi = self._internal_forces(0, fi_init, conc_geom, reinf_geom)[0], self._internal_forces(0, fi_init, conc_geom, reinf_geom)[-1]
        return n1_e, m1_e, n1_fi, m1_fi
    
    def _get_eq_coeff_array(self, eps_cur=0, fi_cur=0, n_cur=0, m_cur=0, n_user=0, m_user=0, 
                            conc_geom=None, reinf_geom=None, tend_geom=None):
        """returns np array with all moments and axial forces
        for computation of linear eq. system in search for corrections of fi and eps"""
        eps_init = GeneralAxBend.EPS_INIT
        #fi_init = self._initial_rotation()
        fi_init = self.fi_init
        n_m_eps_plus_deps_fi_cur = self._internal_forces(eps_cur + eps_init, fi_cur, conc_geom, reinf_geom, tend_geom)[0], \
            self._internal_forces(eps_cur + eps_init, fi_cur, conc_geom, reinf_geom, tend_geom)[-1]
        np_one = np.asanyarray(n_m_eps_plus_deps_fi_cur)
        n_m_eps_fi_cur_plus_dfi =  self._internal_forces(eps_cur, fi_cur + fi_init, conc_geom, reinf_geom, tend_geom)[0], \
            self._internal_forces(eps_cur, fi_cur + fi_init, conc_geom, reinf_geom, tend_geom)[-1]
        np_two = np.asanyarray(n_m_eps_fi_cur_plus_dfi)
        _n_m_cur = self._internal_forces(eps_cur, fi_cur, conc_geom, reinf_geom, tend_geom)
        n_m_cur = _n_m_cur[0], _n_m_cur[-1]
        np_three = np.asanyarray(n_m_cur)
        np_l_array = np.zeros(shape=(2,2))
        np_l_array[0][0] = np_one[0] - np_three[0]
        np_l_array[0][1] = np_two[0] - np_three[0]
        np_l_array[1][0] = np_one[1] - np_three[1]
        np_l_array[1][1] = np_two[1] - np_three[1]
        np_r_array = np.zeros(shape=(2))
        np_r_array[0] = n_user - n_cur
        np_r_array[1] = m_user - m_cur
        return  np_l_array, np_r_array, eps_init, fi_init

    def _update_eps_and_fi(self, eps_cur=0, fi_cur=0, n_cur=0, m_cur=0, conc_geom=None, reinf_geom=None, tend_geom=None):
        n_user = self.n_sd
        m_user = self.m_sd
        np_l_array, np_r_array, eps_init, fi_init = self._get_eq_coeff_array(eps_cur, fi_cur, n_cur, m_cur, n_user, m_user, 
                                                                             conc_geom, reinf_geom, tend_geom)
        le_lfi = self.ETA * self._solve_two_eq(np_l_array, np_r_array)
        # le_lfi = self._solve_two_eq(np_l_array, np_r_array)
        # eps_new = eps_cur + math.copysign(GeneralAxBend.EPS_INIT, le_lfi[0])
        # fi_new = fi_cur + math.copysign(self.fi_init, le_lfi[1])
        eps_new = eps_cur + le_lfi[0] * eps_init
        fi_new = fi_cur + le_lfi[1] * fi_init 
        _c =  self._internal_forces(eps_new, fi_new, conc_geom, reinf_geom, tend_geom)
        n_new, m_new = _c[0], _c[-1]
        return eps_new, fi_new, n_new, m_new
    
    def find_optimal_eps_fi(self, n_it, conc_geom, reinf_geom, tend_geom):
        """search iteratively for best values
        of eps and fi so that M_final, and N_final were
        close to M_sd and N_sd"""
        eps_new = 0
        fi_new = 0
        n_new = 0
        m_new = 0
        for i in range(n_it):
            eps_new, fi_new, n_new, m_new = self._update_eps_and_fi(eps_cur=eps_new, fi_cur=fi_new, n_cur=n_new, m_cur=m_new, 
                                                                    conc_geom=conc_geom, reinf_geom=reinf_geom, tend_geom=tend_geom)
            print(n_new, m_new, i, eps_new, fi_new)
            ## if abs(eps_new) > 0.1 or abs(fi_new) > 0.1:
            ##     eps_new = np.random.uniform(-0.001, 0.001)
            ##     fi_new = np.random.uniform(-0.001, 0.001)
            # check1 = abs(abs(n_new) - abs(self.n_sd)) / (abs(self.n_sd) + 0.005)
            # check2 = abs(abs(m_new) - abs(self.m_sd)) / (abs(self.m_sd) + 0.005)
            # if check1 < 0.01 and check2 < 0.01:
            check1 = abs(abs(n_new) - abs(self.n_sd))
            check2 = abs(abs(m_new) - abs(self.m_sd))
            if check1 < 0.001 and check2 < 0.001:
                break
        return eps_new, fi_new, n_new, m_new

    def alter_n_m(self, tend_geom):
        """"alters M and N if M and N incudes prestressing effects from FE solution envelopes"""
        t_heights, t_areas, n_of_layers = tend_geom
        self.n_sd -= 0.70 * self.R_K_TENDONS * sum(t_areas)
        stress_in_t = len(t_heights) * [0.70 * self.R_K_TENDONS]
        forces_in_t = [stress_in_t[i] * t_areas[i] \
            for i in range(len(stress_in_t))]
        moments_in_t = [forces_in_t[i] * t_heights[i] \
            for i in range(len(stress_in_t))]
        self.m_sd -= sum(moments_in_t)
        return self.m_sd, self.n_sd

def main():
    my_rc_cross_sec = GeneralAxBend(name='GENERAL_CROSS-SECT_no1',
                                b=(0, 1.0, 0), # [m] width of the individual rectangles, b[0] and h[0] are the bottom plate
                                h=(0.0, 1.5, 0.0), # [m] height of the individual rectangles
                                #hsl=0.20, #[m] thickness of upper slab
                                #beff=1.2, #[m] effective width of upper slab
                                cl_conc='C30_37',
                                cl_steel='B500SP',
                                c=25, # [mm]
                                fi=32, # [mm]
                                fi_s=12, # [mm]
                                fi_opp=32, # [mm]
                                nl_reinf_top=(1, (8, 0, 0)), # [mm] denotes number of layers of top reinforcement and corresponding numbers of rebars
                                nl_reinf_bottom=(1, (8, 0 , 0)), # [mm] denotes number of layers of bottom reinforcement and corresponding numbers of rebars
                                m_sd=0, # [MNm]
                                n_sd=0,
                                tendon_info=(1, (0.2, 3, 19, 150)), # (number of tendon layers, 
    #(layer height, no_of_tendons in layer, number of strands in each tendon, area if single strand))
                                prestr_ef_in_mn = True)
    
    # my_rc_cross_sec1a = GeneralAxBend(name='GENERAL_CROSS-SECT_no1a',  # sprawdzenie na prostokącie symetrii odpowiedzi w przekroju symetrycznym
    #                             b=(0, 1.0, 0), # [m] width of the individual rectangles
    #                             h=(0.0, 1.5, 0.0), # [m] height of the individual rectangles
    #                             #hsl=0.20, #[m] thickness of upper slab
    #                             #beff=1.2, #[m] effective width of upper slab
    #                             cl_conc='C30_37',
    #                             cl_steel='B500SP',
    #                             c=25, # [mm]
    #                             fi=32, # [mm]
    #                             fi_s=12, # [mm]
    #                             fi_opp=32, # [mm]
    #                             nl_reinf_top=(1, (10, 0, 0)), # [mm] denotes number of layers of top reinforcement and corresponding numbers of rebars
    #                             nl_reinf_bottom=(1, (10, 0 , 0)), # [mm] denotes number of layers of bottom reinforcement and corresponding numbers of rebars
    #                             m_sd=-3, # [MNm]
    #                             n_sd=-0.5) # [MN]
    
    # my_rc_cross_sec2 = GeneralAxBend(name='GENERAL_CROSS-SECT_no2',
    #                             b=(0, 1.0, 2.5), # [m] width of the individual rectangles
    #                             h=(0, 1.85, 0.3), # [m] height of the individual rectangles
    #                             #hsl=0.20, #[m] thickness of upper slab
    #                             #beff=1.2, #[m] effective width of upper slab
    #                             cl_conc='C30_37',
    #                             cl_steel='B500SP',
    #                             c=25, # [mm]
    #                             fi=32, # [mm]
    #                             fi_s=12, # [mm]
    #                             fi_opp=12, # [mm]
    #                             nl_reinf_top=(1, (25, 0, 0)), # [mm] denotes number of layers of top reinforcement and corresponding numbers of rebars
    #                             nl_reinf_bottom=(1, (8, 0 , 0)), # [mm] denotes number of layers of bottom reinforcement and corresponding numbers of rebars
    #                             m_sd=3, # [MNm]
    #                             n_sd=-3) # [MN]

    my_rc_cross_sec2a = GeneralAxBend(name='GENERAL_CROSS-SECT_no2a',
                                b=(0, 1.00, 2.0), # [m] width of the individual rectangles
                                h=(0, 1.20, 0.250), # [m] height of the individual rectangles
                                #hsl=0.20, #[m] thickness of upper slab
                                #beff=1.2, #[m] effective width of upper slab
                                cl_conc='C35_45',
                                cl_steel='B500SP',
                                c=25, # [mm]
                                fi=25, # [mm]
                                fi_s=12, # [mm]
                                fi_opp=25, # [mm]
                                nl_reinf_top=(1, (10, 0, 0)), # [mm] denotes number of layers of top reinforcement and corresponding numbers of rebars
                                nl_reinf_bottom=(1, (10, 0 , 0)), # [mm] denotes number of layers of bottom reinforcement and corresponding numbers of rebars
                                m_sd=3, # [MNm]
                                n_sd=-1,
                                tendon_info=(1, (0.2, 3, 19, 150)),
                                prestr_ef_in_mn=False)
    
    my_rc_cross_sec2b = GeneralAxBend(name='GENERAL_CROSS-SECT_no2a',
                                b=(3.00, 1.00, 0), # [m] width of the individual rectangles
                                h=(0.25, 1.20, 0), # [m] height of the individual rectangles
                                #hsl=0.20, #[m] thickness of upper slab
                                #beff=1.2, #[m] effective width of upper slab
                                cl_conc='C35_45',
                                cl_steel='B500SP',
                                c=25, # [mm]
                                fi=25, # [mm]
                                fi_s=12, # [mm]
                                fi_opp=25, # [mm]
                                nl_reinf_top=(1, (10, 0, 0)), # [mm] denotes number of layers of top reinforcement and corresponding numbers of rebars
                                nl_reinf_bottom=(1, (10, 0 , 0)), # [mm] denotes number of layers of bottom reinforcement and corresponding numbers of rebars
                                m_sd=2, # [MNm]
                                n_sd=1, # [MN]
                                tendon_info=(1, (0.5, 3, 19, 150)),
                                prestr_ef_in_mn=False) # [MN]
    
    # my_rc_cross_sec3 = GeneralAxBend(name='GENERAL_CROSS-SECT_no2',
    #                             b=(1.2, 0.6, 1.2), # [m] width of the individual rectangles
    #                             h=(0.4, 1.00, 0.25), # [m] height of the individual rectangles
    #                             #hsl=0.20, #[m] thickness of upper slab
    #                             #beff=1.2, #[m] effective width of upper slab
    #                             cl_conc='C30_37',
    #                             cl_steel='B500SP',
    #                             c=25, # [mm]
    #                             fi=20, # [mm]
    #                             fi_s=12, # [mm]
    #                             fi_opp=32, # [mm]
    #                             nl_reinf_top=(1, (12, 0, 0)), # [mm] denotes number of layers of top reinforcement and corresponding numbers of rebars
    #                             nl_reinf_bottom=(1, (8, 0 , 0)), # [mm] denotes number of layers of bottom reinforcement and corresponding numbers of rebars
    #                             m_sd=5, # [MNm]
    #                             n_sd=2) # [MN]
    
    my_rc_cross_sec3a = GeneralAxBend(name='GENERAL_CROSS-SECT_no3a',
                                b=(2, 1.2, 3), # [m] width of the individual rectangles
                                h=(0.25, 1.20, 0.25), # [m] height of the individual rectangles
                                #hsl=0.20, #[m] thickness of upper slab
                                #beff=1.2, #[m] effective width of upper slab
                                cl_conc='C35_45',
                                cl_steel='B500SP',
                                c=25, # [mm]
                                fi=25, # [mm]
                                fi_s=12, # [mm]
                                fi_opp=25, # [mm]
                                nl_reinf_top=(1, (10, 0, 0)), # [mm] denotes number of layers of top reinforcement and corresponding numbers of rebars
                                nl_reinf_bottom=(1, (10, 0 , 0)), # [mm] denotes number of layers of bottom reinforcement and corresponding numbers of rebars
                                m_sd=3, # [MNm]
                                n_sd=2, # [MN]
                                tendon_info=(1, (0.5, 3, 20, 150)),
                                prestr_ef_in_mn=False) # [MN]
    
    my_rc_cross_sec3b = GeneralAxBend(name='GENERAL_CROSS-SECT_no3b',
                                b=(3, 1.2, 3), # [m] width of the individual rectangles
                                h=(0.25, 1.20, 0.25), # [m] height of the individual rectangles
                                #hsl=0.20, #[m] thickness of upper slab
                                #beff=1.2, #[m] effective width of upper slab
                                cl_conc='C35_45',
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

    cross_sect = my_rc_cross_sec3b
    tend_geom = cross_sect._tendon_geom()
    if cross_sect.prestr_ef_in_mn:
        cross_sect.alter_n_m()
    conc_geom = cross_sect._conc_layers()
    reinf_geom = cross_sect._reinf_geom()
    inter_forces_data1 = cross_sect.find_optimal_eps_fi(100, conc_geom, reinf_geom, tend_geom)
    eps_cur, fi_cur = inter_forces_data1[0], inter_forces_data1[1]
    inter_forces_data = cross_sect._internal_forces(eps_cur, fi_cur, conc_geom, reinf_geom, tend_geom)

    GeneralAxBend.trial_plot(inter_forces_data[7], inter_forces_data[4], 'strains in steel')
    GeneralAxBend.trial_plot(inter_forces_data[7], inter_forces_data[5], 'stress in steel')
    GeneralAxBend.trial_plot(inter_forces_data[7], inter_forces_data[6], 'forces in steel')
    GeneralAxBend.trial_plot(inter_forces_data[11], inter_forces_data[8], 'strains in tendons')
    GeneralAxBend.trial_plot(inter_forces_data[11], inter_forces_data[9], 'stress in tendons')
    GeneralAxBend.trial_plot(inter_forces_data[11], inter_forces_data[10], 'forces in tendons')
    GeneralAxBend.trial_plot(inter_forces_data[15], inter_forces_data[12], 'strains in concrete')
    GeneralAxBend.trial_plot(inter_forces_data[15], inter_forces_data[13], 'stress in concrete')
    GeneralAxBend.trial_plot(inter_forces_data[15], inter_forces_data[14], 'forces in concrete')
    # #print('pure in forces:', inter_forces_data[0], inter_forces_data[-1])
    # # inter_forces_data1 = my_rc_cross_sec._update_eps_and_fi(eps_cur=-0.13863684678772847, fi_cur=0.16516223687652937, n_cur=-4.282748843304599, m_cur=1.918676231783936)
    # # print('pure in forces:', inter_forces_data1)

    # print(my_rc_cross_sec._tendon_geom())
    # print(inter_forces_data[8])
    # print(inter_forces_data[11])

if __name__ == '__main__':
    main()


# ROZWAŻ NACHYLENIE PŁASKICH PÓŁEK !!!