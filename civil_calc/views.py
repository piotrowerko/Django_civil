from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from civil_calc.models import Simple_c_calc
from .serializers import Simple_c_calcSerializer
from rest_framework import viewsets
import json


from .deep_backend.calc_pio2 import CalcPio2
from .deep_backend.rect_single_reinf import RectCrSectSingle

@api_view(["GET", "POST"])  # parsing is done automatically
def welcome(request):
    # content = request.data
    # aa = JsonResponse(content)
    # # bb = aa.data
    # # cc = bb["first_number"] + bb["second_number"]
    # # dd = {"sum": cc}
    # return aa
    if request.method == 'POST':
        return Response({"message": "Got some data!", "data": request.data})
    return Response({"message": "Hello, world!"})

@api_view(["GET", "POST"])
def sum_data(request):
    # content = request.data
    # aa = JsonResponse(content)
    # # bb = aa.data
    # # cc = bb["first_number"] + bb["second_number"]
    # # dd = {"sum": cc}
    # return aa
    if request.method == 'POST':
        pp = request.body
        cc = request.data
        dd = cc["first_number"] + cc["second_number"]
        ee = {'sum': dd}
        return JsonResponse(ee)  #, safe=False)
    return JsonResponse({"message": "No data received!"})

@api_view(["GET", "POST"])
def comp_data(request):
    # content = request.data
    # aa = JsonResponse(content)
    # # bb = aa.data
    # # cc = bb["first_number"] + bb["second_number"]
    # # dd = {"sum": cc}
    # return aa
    if request.method == 'POST':
        cc = request.data
        # dd = cc["first_number"] + cc["second_number"]
        inst_Calc = CalcPio2()
        dd = inst_Calc._sum(cc["first_number"], cc["second_number"])
        ee = {'sum': dd}
        return JsonResponse(ee)  #, safe=False)
    return JsonResponse({"message": "No data received!"})

@api_view(["GET", "POST"])
def rect_reinf(request):
    if request.method == 'POST':
        cc = request.data
        my_cross_sect = RectCrSectSingle(name=cc['name'],
                                b=cc['b'],
                                h=cc['h'],
                                cl_conc=cc['cl_conc'],
                                cl_steel=cc['cl_steel'],
                                c=cc['c'],
                                fi=cc['fi'],
                                no_of_bars=cc['no_of_bars'],
                                fi_s=cc['fi_s'])
        _dd = my_cross_sect.compute_m_rd_single_r()
        _ee = {
            'm_rd': _dd[0],  # nośność przekroju na zginanie
            'ksi_eff': _dd[1],  # względne położenie osi obojętnej przekroju
            'x_eff': _dd[2],  # wysokość strefy ściskanej
            }
        return JsonResponse(_ee)
    return JsonResponse({"message": "No data received!"})





# class Simple_c_calcViewSet(viewsets.ModelViewSet):
#     queryset = Simple_c_calc.objects.all()
#     serializer_class = Simple_c_calcSerializer
    
#     # def retrieve(self, request, *args, **kwargs):
#     #     ret = super(Simple_c_calcViewSet, self).list(request)
#     #     return JsonResponse({"ret": ret}, safe=False)

#     # def list(self, request, *args, **kwargs):
#     #     return JsonResponse({"request": request}, safe=False)