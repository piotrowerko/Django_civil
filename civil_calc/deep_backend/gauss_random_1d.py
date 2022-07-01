#NOWAK STRONA 82 !! metoda polega na poszukiwaniu zbioru vektorów własnych (tj. macierz T) macierzy kowariancji Cx
# modelowanych, skolerowanych zmiennych losowych Xi
# dzięki temu możemy wylosować całkowicie nieskolerowane zmienne losowe Yi i przemnożyć Y * T by otrzymać losowy
# zestaw odpowiednio skoleoranych zmiennych Xi które stanowią wartości wsodowe punktów siatki pola losowego

import numpy as np
import matplotlib.pyplot as plt


class RandomField1D():
    """
    it's instance is a single realization
    of 1d random field
    """
    def __init__(self, 
                 mi, 
                 mean, 
                 no_of_var,
                 member_length,
                 corr_radius):
        self.mi = mi
        self.mean = mean
        self.no_of_var = no_of_var # number of desired random variables in the random field
        self.member_length = member_length
        self.corr_radius = corr_radius
        self.sigma_x = mean * mi
    
    def corr_coeff_array(self, no_of_var):
        ro = np.eye(no_of_var)
        delta_x = self.member_length / (no_of_var + 1)
        for a in range(no_of_var):
            for b in range(no_of_var):
                __aa = np.exp(-(abs(a - b) * delta_x) \
                    / self.corr_radius)
                ro[a,b] = __aa
        cx = ro * self.sigma_x * self.sigma_x
        return ro, cx
    
    def tt_mean_yi(self, cx):
        eigenvalues, eigenvectors = np.linalg.eig(cx)
        __t = - eigenvectors
        __tt = np.transpose(__t)
        mean_xi = np.full((self.no_of_var, 1), self.mean)
        mean_yi = np.matmul(__tt, mean_xi)
        return __t, __tt, mean_yi
    
    def cy_sigma_yi(self, __tt, cx, __t):
        cy = np.linalg.multi_dot([__tt, cx, __t])
        sigma_yi = np.sqrt(cy)
        return cy, sigma_yi
    
    def compute_xi(self, no_of_var, mean_yi, cy, __t):
        yi = np.zeros((no_of_var, 1))
        for ww in range(no_of_var):
            _aa=np.random.normal(mean_yi[ww], np.sqrt(cy[ww,ww]),size=(1))
            yi[ww,0] = _aa
        xi=np.matmul(__t, yi)
        return xi 
    
def main():
    my_first_1d_rf_instance = RandomField1D(mi=0.3,
                                            mean=10,
                                            no_of_var=15,
                                            member_length=6,
                                            corr_radius=60)
    
    ro, cx = my_first_1d_rf_instance.corr_coeff_array(my_first_1d_rf_instance.no_of_var)
    #print(ro)
    #print(cx)
    __t, __tt, mean_yi = my_first_1d_rf_instance.tt_mean_yi(cx)
    #print(mean_yi)
    cy, sigma_yi = my_first_1d_rf_instance.cy_sigma_yi( __tt, cx, __t)
    #print(sigma_yi)
    xi = my_first_1d_rf_instance.compute_xi(my_first_1d_rf_instance.no_of_var, 
                                            mean_yi, 
                                            cy, 
                                            __t)
    print(xi)

if __name__ == '__main__':
    main()