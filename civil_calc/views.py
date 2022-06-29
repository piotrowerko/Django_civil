import json

from rest_framework import status
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Simple_c_calc, JsonUserQuery
from .serializers import Simple_c_calcSerializer, JsonUserQuerySerializer

from .deep_backend.calc_pio2 import CalcPio2
from .deep_backend.rect_single_reinf import RectCrSectSingle
from .deep_backend.rect_double_reinf import RectCrSectDoubleR
from .deep_backend.rect_find_reinf import RectCrReinf
from .deep_backend.t_sect_ben_reinf import TCrReinf

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
    if request.method == 'POST':
        cc = request.data
        dd = cc["first_number"] + cc["second_number"]
        ee = {'sum': dd}
        return JsonResponse(ee)  #, safe=False)
    return JsonResponse({"message": "No data received!"})


@api_view(["POST"])
@permission_classes((IsAuthenticated, ))
def sum_data_and_save(request):
    """saves json body post to db and returns sum of two numbers"""
    aa = 1
    json_query = JsonUserQuery(owner=request.user)
    if request.method == 'POST':
        data=request.data
        serializer = JsonUserQuerySerializer(json_query, data=data)
        data = {}
        if serializer.is_valid():
            dd = serializer.initial_data["the_json"]["first_number"] + serializer.initial_data["the_json"]["second_number"]
            ee = {'sum': dd}
            serializer.save()
            return Response(ee, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(["GET", "POST"])
def comp_data(request):
    aa = 1
    if request.method == 'POST':
        cc = request.data
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

@api_view(["GET", "POST"])
@permission_classes((IsAuthenticated, ))
def comp_data_three(request):
    if request.method == 'POST':
        cc = request.data
        inst_Calc = CalcPio2()
        dd = inst_Calc._sum(cc["first_number"],
                            cc["second_number"], 
                            cc["third_number"])
        ee = {'sum': dd}
        return JsonResponse(ee)  #, safe=False)
    return JsonResponse({"message": "No data received!"})

@api_view(["GET", "POST"])
def rect_double_reinf(request):
    if request.method == 'POST':
        cc = request.data
        my_cross_sect = RectCrSectDoubleR(name=cc['name'],
                                b=cc['b'],
                                h=cc['h'],
                                cl_conc=cc['cl_conc'],
                                cl_steel=cc['cl_steel'],
                                c=cc['c'],
                                fi=cc['fi'],
                                no_of_bars=cc['no_of_bars'],
                                fi_s=cc['fi_s'],
                                fi_opp=cc['fi_opp'],
                                no_of_opp_bars=cc['no_of_opp_bars'])
        _dd = my_cross_sect.compute_m_rd_double_r()
        _ee = {
            'm_rd': _dd[0],  # nośność przekroju na zginanie
            'ksi_eff': _dd[1],  # względne położenie osi obojętnej przekroju
            'x_eff': _dd[2],  # wysokość strefy ściskanej
            }
        return JsonResponse(_ee)
    return JsonResponse({"message": "No data received!"})


@api_view(["GET", "POST"])
def rect_find_reinf(request):
    if request.method == 'POST':
        cc = request.data
        my_cross_sect = RectCrReinf(name=cc['name'],
                                b=cc['b'],
                                h=cc['h'],
                                cl_conc=cc['cl_conc'],
                                cl_steel=cc['cl_steel'],
                                c=cc['c'],
                                fi=cc['fi'],
                                fi_s=cc['fi_s'],
                                fi_opp=cc['fi_opp'],
                                m_sd=cc['m_sd'])
        _dd = my_cross_sect.compute_reinf_rect()
        _ee = {
            'As1': _dd[0],
            'ns1': _dd[1],
            'As2': _dd[2],
            'ns2': _dd[3],
            'remark': _dd[4]
            }
        return JsonResponse(_ee)
    return JsonResponse({"message": "No data received!"})


@api_view(["GET", "POST"])
def t_sect_ben_reinf(request):
    if request.method == 'POST':
        cc = request.data
        my_cross_sect = TCrReinf(name=cc['name'],
                                b=cc['b'],
                                h=cc['h'],
                                hsl=cc['h_sl'], #[m] thickness of upper slab
                                beff=cc['b_eff'], #[m] effective width of upper slab
                                cl_conc=cc['cl_conc'],
                                cl_steel=cc['cl_steel'],
                                c=cc['c'],
                                fi=cc['fi'],
                                fi_s=cc['fi_s'],
                                fi_opp=cc['fi_opp'],
                                m_sd=cc['m_sd'])
        _dd = my_cross_sect.compute_reinf_T()
        if _dd[0][4] != _dd[1]:  # rectangle case
            _ee = {
                'As1': _dd[0][0],
                'ns1': _dd[0][1],
                'As2': _dd[0][2],
                'ns2': _dd[0][3],
                'remark': _dd[0][4],
                'remark2': _dd[1]
                }
        else:  # real T case
            _ee = {
                'As1': _dd[0][0],
                'ns1': _dd[0][1],
                'As2': _dd[0][2],
                'ns2': _dd[0][3],
                'remark': _dd[0][4],
                }
        return JsonResponse(_ee)
    return JsonResponse({"message": "No data received!"})

@api_view(['GET', ])
@permission_classes((IsAuthenticated, ))
def show_json_user_query(request, slug):
    """shows specific json user query"""
    try:
        json_user_query = JsonUserQuery.objects.get(slug=slug)
    except JsonUserQuery.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = JsonUserQuerySerializer(json_user_query)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def save_jsonquery_view(request):
    """saves defined json to the database"""
    json_query = JsonUserQuery(owner=request.user)

    if request.method == 'POST':
        
        serializer = JsonUserQuerySerializer(json_query, data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class JsonInputsListView(ListAPIView):
    """
    https://www.youtube.com/watch?v=O79lhytiKd0&list=PLgCYzUzKIBE9Pi8wtx8g55fExDAPXBsbV&index=10
    https://www.youtube.com/watch?v=F0tfRtBEkck&list=PLgCYzUzKIBE9Pi8wtx8g55fExDAPXBsbV&index=11
    """
    queryset = JsonUserQuery.objects.all()
    serializer_class = JsonUserQuerySerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('title', 'the_json', 'owner__username')


# @api_view(['GET',])
# @permission_classes((IsAuthenticated,))
# def api_is_author_of_blogpost(request, slug):
#     try:
#         blog_post = BlogPost.objects.get(slug=slug)
#     except BlogPost.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)

#     data = {}
#     user = request.user
#     if blog_post.author != user:
#         data['response'] = "You don't have permission to edit that."
#         return Response(data=data)
#     data['response'] = "You have permission to edit that."
#     return Response(data=data)


# # Response: https://gist.github.com/mitchtabian/a97be3f8b71c75d588e23b414898ae5c
# # Url: https://<your-domain>/api/blog/<slug>/delete
# # Headers: Authorization: Token <token>
# @api_view(['DELETE',])
# @permission_classes((IsAuthenticated, ))
# def api_delete_blog_view(request, slug):

#     try:
#         blog_post = BlogPost.objects.get(slug=slug)
#     except BlogPost.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)

#     user = request.user
#     if blog_post.author != user:
#         return Response({'response':"You don't have permission to delete that."}) 

#     if request.method == 'DELETE':
#         operation = blog_post.delete()
#         data = {}
#         if operation:
#             data['response'] = DELETE_SUCCESS
#         return Response(data=data)





# class Simple_c_calcViewSet(viewsets.ModelViewSet):
#     queryset = Simple_c_calc.objects.all()
#     serializer_class = Simple_c_calcSerializer
    
#     # def retrieve(self, request, *args, **kwargs):
#     #     ret = super(Simple_c_calcViewSet, self).list(request)
#     #     return JsonResponse({"ret": ret}, safe=False)

#     # def list(self, request, *args, **kwargs):
#     #     return JsonResponse({"request": request}, safe=False)
