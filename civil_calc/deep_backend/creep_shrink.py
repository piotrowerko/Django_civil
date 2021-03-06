import math
import numpy as np
import matplotlib.pyplot as plt

from . rect_single_reinf import RectCrSectSingle

class CreepShrink():
    """creep and shrinkage computations"""

    def __init__(self, name, cl_conc, ac, 
                 u, t0, temp, rh, cement_class, ts):
        self.name = name
        self.cl_conc = cl_conc
        self.ac = ac  # Concrete cross-sectional area [m2]
        self.u = u  # Part of cross-section perimeter exposed to drying [m]
        self.t0 = t0  # Age of concrete at loading
        self.temp = temp  # Ambient temperature oC
        self.rh = rh  # Relative humidity of ambient environment %
        self.cement_class = cement_class  # Cement type (class_S, class_N, class_R)
        self.ts = ts  # Age of concrete at end of curing
        self.h0 = 1000 * 2 * ac / u
        self.fcm = self.get_fc(csv_row=4)
        self.fck = self.get_fc(csv_row=1)
        self.e_cm = self.get_fc(csv_row=9)
        
    def __str__(self) -> str:
        return f'my name is {self.name}, my conc. class is {self.cl_conc}'
    
    #@property
    def get_fc(self, csv_row=4):
        """returns chosen f_c value according to EC"""
        conc_data = RectCrSectSingle.load_concrete(
            file_path='civil_calc/deep_backend/concrete_ec.csv')
        conc_class_names = [el[0] for el in conc_data]
        class_ind = conc_class_names.index(self.cl_conc)
        fc = float(conc_data[class_ind][csv_row])
        return fc

    def kh(self, h0):
        """returns kh coefficient"""
        if h0 >= 500:
            kh = 0.70
        elif h0 < 100:
            kh = 1
        else:
            kh = 3 * 10 ** -6 * h0 ** 2 - 0.0023 * h0 + 1.2
        return kh
    
    def _beta_rh(self, rh):
        """returns beta_rh coefficient"""
        beta_rh = 1.55 * (1 - (rh / 100)**3)
        return beta_rh

    def _alphas(self, fcm):
        """eq. B.8C s. 185 in EN-1992-1-1:2004+AC2008"""
        alpha_1 = (35 / fcm) ** 0.7
        alpha_2 = (35 / fcm) ** 0.2
        alpha_3 = (35 / fcm) ** 0.5
        return alpha_1, alpha_2, alpha_3
    
    def _fi_rh(self, alpha_1, alpha_2):
        """factor ??RH accounts for the effect of relative humidity,
        eq. B.3A, B.3B s. 185 in EN-1992-1-1:2004+AC2008"""
        if self.fcm <= 35:
            fi_rh = 1 + (1 - self.rh / 100) \
                / (0.1 * (self.h0) ** (1 / 3))
        else:
            fi_rh = (1 + ((1 - self.rh / 100) \
                / (0.1 * (self.h0) ** (1 / 3))) * alpha_1) * alpha_2
        return fi_rh
    
    def _t0r(self, cement_class):
        """returns modified age of concrete at loading
        due to cement class
        eq. B.9, s. 186 in EN-1992-1-1:2004+AC2008"""
        if cement_class.upper() == 'S':
            alpha = -1
        elif cement_class.upper() == 'N':
            alpha = 0
        else:  # cement_class.upper() == 'R':
            alpha = 1
        t0r = self.t0 * ((9 / (2 + self.t0 ** 1.2)) + 1) ** alpha
        if t0r < 0.5:
            t0r = 0.5
        return t0r
    
    def beta_fcm_beta_t0r(self, t0r):
        """coefficient ??(fcm) allows for the effect of concrete strength. 
        EN1992-1-1 eq. B.4 as ??(fcm)
        coefficient ??(t0) allows for the effect of concrete age at loading. 
        EN1992-1-1 eq. B.5 as ??(t0)"""
        beta_fcm = 16.8 / (self.fcm ** 0.5)
        beta_t0r = 1 / (0.1 + t0r ** 0.20)
        return beta_fcm, beta_t0r
    
    def fi_0(self, alphas, t0r):
        """notional creep coefficient ??0
        EN1992-1-1 eq. B.2"""
        beta_fcm, beta_t0r = self.beta_fcm_beta_t0r(t0r)
        fi_rh = self._fi_rh(alphas[0], alphas[1])
        fi_0 = fi_rh * beta_fcm * beta_t0r
        return fi_0
    
    def beta_h(self, alphas):
        """coefficient ??H depends on the relative 
        humidity RH and the notional member size h0. 
        EN1992-1-1 eq. B.8a, B.8b"""
        if self.fcm <= 35:
            beta_h = 1.5 * (1 + (0.012 * self.rh) ** 18) \
                * self.h0 + 250
            if beta_h > 1500:
                beta_h = 1500 
        else:
            beta_h = 1.5 * (1 + (0.012 * self.rh) ** 18) \
                * self.h0 + 250 * alphas[2]
            if beta_h > 1500 * alphas[2]:
                beta_h = 1500 * alphas[2]
        return beta_h

    def beta_t_t0(self, t, alphas):
        """time-development coefficient ??(t,t0) for creep
        EN1992-1-1 eq. B.7
        t - time in days"""
        beta_h = self.beta_h(alphas)
        beta_t_t0 = ((t - self.t0) / (beta_h + t - self.t0)) ** 0.30
        return beta_t_t0
    
    def fi_t_t0(self, t, alphas, t0r):
        """creep coefficient at given time t
        EN1992-1-1 s. 185, eq. B.1"""
        beta_t_t0 = self.beta_t_t0(t, alphas)
        fi_0 = self.fi_0(alphas, t0r)
        fi_t_t0 = fi_0 * beta_t_t0
        return fi_t_t0
    
    def beta_ds_t_ts(self, t):
        """time-development coefficient ??ds(t,ts) for shrinkage
        EN1992-1-1, s. 29, eq. 3.10
        t - time in days"""
        beta_ds_t_ts = (t - self.ts) \
            / (t - self.ts + 0.04 * self.h0 ** (3 / 2))
        return beta_ds_t_ts

    # nominalne odkszta??cenie skurczu przy wysychaniu
    def eps_cd_0(self, cement_class):
        """returns basic drying shrinkage strain
        source: eq. B.11 s.186 in EN-1992-1-1:2004+AC2008"""
        if cement_class.upper() == 'S':
            alpha_ds1 = 3
            alpha_ds2 = 0.13
        elif cement_class.upper() == 'N':
            alpha_ds1 = 4
            alpha_ds2 = 0.12
        else:  # cement_class.upper() == 'R':
            alpha_ds1 = 6
            alpha_ds2 = 0.11
        f_cm = self.fcm
        beta_rh = self._beta_rh(self.rh)
        eps_cd_0 = 0.85 * (220 + 110 * alpha_ds1) * \
            math.e ** (- alpha_ds2 * f_cm / 10) * beta_rh * 10 ** - 6
        return eps_cd_0
    
    def eps_cd_t(self, t):
        """time-development curve of the drying shrinkage strain 
        ??cd(t) as a function of time t 
        EN1992-1-1 eq. 3.9"""
        beta_ds_t_ts = self.beta_ds_t_ts(t)
        eps_cd_0 = self.eps_cd_0(self.cement_class)
        kh = self.kh(self.h0)
        eps_cd_t = beta_ds_t_ts * kh * eps_cd_0
        return eps_cd_t

    # odkszta??cenia od skurczu autogenicznego

    def eps_ca_inf(self):
        """returns autogenous shrinkage strain at infinite time
        EN1992-1-1 equation 3.11"""
        eps_ca_inf = 2.5 * (self.fck - 10) * 10 ** -6
        return eps_ca_inf

    def eps_ca_t(self, t):
        """returns autogenous shrinkage strain at given time
        EN1992-1-1 equation 3.12"""
        eps_ca_inf = self.eps_ca_inf()
        beta_as_t = 1 - math.e ** (-0.2 * t ** 0.5)
        eps_ca = eps_ca_inf * beta_as_t
        return eps_ca

    # ca??kowite odkszta??cenie skurczowe 
    
    def eps_cs_t(self, t):
        """total shrinkage strain ??cs is composed
        from the drying shrinkage strain ??cd and 
        the autogenous shrinkage strain 
        ??c as specified in EN1992-1-1 eq. 3.8:"""
        eps_ca_t = self.eps_ca_t(t)
        eps_cd_t = self.eps_cd_t(t)
        eps_cs_t = eps_ca_t + eps_cd_t
        return eps_cs_t

    def compute_arrays(self, alphas, t0r):
        """returns 3 arrays: 
        1. time [days]
        2. Creep coefficient [-]
        3. Shrinkage strain [-]*10**-5"""
        time_arr = np.arange(1, 365*100, 1, dtype=np.float64)
        creep_arr = np.zeros([self.t0])
        shrink_arr = np.array([])
        for t in time_arr:
            if t > self.t0:
                creep_arr = np.append(creep_arr, [self.fi_t_t0(t, alphas, t0r)])
            shrink_arr = np.append(shrink_arr, [self.eps_cs_t(t)])
        return time_arr, creep_arr, shrink_arr

def main():
    # my_member = CreepShrink(name='my_member1', cl_conc='C50_60', 
    #                         ac=4.41, u=9.78, 
    #                         t0=14, temp=20, rh=80,
    #                         cement_class='R', ts=3)
    my_member = CreepShrink(name='my_member1', cl_conc='C30_37', 
                        ac=1, u=2, 
                        t0=7, temp=20, rh=70,
                        cement_class='N', ts=7)
    print(f'h0 = {my_member.h0}')
    print(f'kh = {my_member.kh(my_member.h0)}')
    print(f'beta_rh = {my_member._beta_rh(my_member.rh)}')
    print(f'fcm = {my_member.fcm}')
    print(f'eps_cd_0 = {my_member.eps_cd_0(cement_class="R")}')
    
    alphas = my_member._alphas(my_member.fcm)
    
    print(f'alphas = {alphas}')
    print(f'fi_rh = {my_member._fi_rh(alphas[0], alphas[1])}')
    
    t0r = my_member._t0r(cement_class=my_member.cement_class)
    
    print(f't0r = {t0r}')
    print(f'beta_fcm, beta_t0r = {my_member.beta_fcm_beta_t0r(t0r)}')
    print(f'fi_0 = {my_member.fi_0(alphas, t0r)}')
    print(f'beta_h = {my_member.beta_h(alphas)}')
    print(f'beta_t_t0 = {my_member.beta_t_t0(100 * 365, alphas)}')
    print(f'fi_t_t0 = {my_member.fi_t_t0(100 * 365, alphas, t0r)}')
    print(f'beta_ds_t0_ts = {my_member.beta_ds_t_ts(t=my_member.t0)}')
    print(f'eps_cd_t0 = {my_member.eps_cd_t(t=my_member.t0)}')
    print(f'beta_ds_t100_ts = {my_member.beta_ds_t_ts(t=365*100)}')
    print(f'eps_cd_t100 = {my_member.eps_cd_t(t=365*100)}')
    print(f'eps_ca_inf =  {my_member.eps_ca_inf()}')
    print(f'eps_ca_t=14 = {my_member.eps_ca_t(t=my_member.t0)}')
    print(f'eps_cs_t=14 = {my_member.eps_cs_t(t=my_member.t0)}')
    print(f'eps_cs_t=14 = {my_member.eps_cs_t(t=365*100)}')
    
    time_arr, creep_arr, shrink_arr = my_member.compute_arrays(alphas, t0r)
    
    fig0, ax0 = plt.subplots()
    fig0.set_size_inches(9, 6)
    ax1 = ax0.twinx()
    pp1 = ax0.plot(time_arr, creep_arr, 
                   label='Creep coef. development curve')
    pp2 = ax1.plot(time_arr, shrink_arr*100000, 
                   label='Shrinkage development curve [x10^-5]', color='orange')
    pp = pp1 + pp2
    ax0.set_title('Creep and shrinkage development curves')
    ax0.xaxis.grid(True, which='major')
    ax0.yaxis.grid(True, which='major')
    ax0.set_xlabel('Time [days]', fontsize=15)
    ax0.set_ylabel('Creep coeff. [-]', fontsize=15)
    ax1.set_ylabel('Shrinkage strain x10**-5 [-]', fontsize=15)
    #plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), 
    # fancybox=True, shadow=True, ncol=2, fontsize=10)
    labs = [l.get_label() for l in pp]
    ax0.legend(pp, labs, loc='upper center', bbox_to_anchor=(0.5, -0.05), 
               fancybox=True, shadow=True, ncol=2, fontsize=13)
    ax0.tick_params(labelsize=15)
    ax1.tick_params(labelsize=15)
    plt.show()

    
if __name__ == '__main__':
    main()
