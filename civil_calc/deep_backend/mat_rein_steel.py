# https://www.muratorplus.pl/technika/konstrukcje/stal-zbrojeniowa-gatunki-stali-zbrojeniowej-znakowanie-cena-aa-QTVb-wFff-8Bk9.html

class ReinSteel():
    """data regarding steel properties
    fyk, fyd, epsilon, ksiefflim"""
    REIN_STEEL_DATA = {
    'BSt500S' : (500, 435, 2.1, 0.5, "b", 0.05, 0.08),  # fyk, fyd, E, ksi_eff_lim, ductility class, espilon_u_k, k
    'B500SP' : (500, 435, 2.1, 0.5, "c", 0.075, 0.15) # fyk, fyd, E, ksi_eff_lim, ductility class
    }