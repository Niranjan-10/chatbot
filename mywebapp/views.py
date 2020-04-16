from django.shortcuts import render
# import urllib
from django.http import HttpResponse, JsonResponse
import json
from six import text_type
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from pyzipcode import ZipCodeDatabase
import pgeocode
import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib.request
# from urllib3 import urlretrieve
from tabula import read_pdf, convert_into
import os
import re
from mychatbot.settings import DOCFILES_FOLDER

# Create your views here.
def home(request):
    return render(request,'home.html')

@csrf_exempt
def getinfo(request):
    nomi = pgeocode.Nominatim('IN')
    
    
    if request.method == 'POST':

        # req = request.get_json(silent=True, force=True)
        # result = req.get("queryResult")
        # print(result)
        # name = request.POST.get('name')
        # email = request.POST.get('email')
        # zipcode = request.POST.get('zipcode')
        # mobile = request.POST.get('mobile')
        data = json.loads(request.body)
        # for google dialogflow

        # print(data['queryResult']['parameters'])
        # name = data['queryResult']['parameters']['name']
        # email = data['queryResult']['parameters']['email']
        # mobile = data['queryResult']['parameters']['mobile']
        # zipcode = data['queryResult']['parameters']['zipcode']

        # for aws lex
        name = data['name']
        email = data['email']
        mobile = data['mobile']
        zipcode = data['zipcode']
        print(name)
        zipcode_info = nomi.query_postal_code(zipcode)
        print(zipcode)
        print('-'*20)
        zipcode_info = nomi.query_postal_code(zipcode)
        # print(zipcode)
        # print('-'*20)
        # print(zipcode_info)
        # intent_name = result.get("intent").get('displayName')
        
        try:
            if type(zipcode_info['place_name']) is list:
                city_name = zipcode_info['place_name'].split(',')
                # print(city_name)
            else:
                city_name = zipcode_info['place_name'].split(',')
                # print(city_name)
        except:
            return HttpResponse('not valid pincode')
        
        state_name = zipcode_info['state_name']
        # print(state_name)
        # print(type(city_name))
        patient_data=getPatientInformation(state_name,city_name)
        nation_data = getNationData()
        world_data = getWorldWideData()
        state_data = getStateData(state_name)
        # getStateData(state_name)
        # print(patient_data)
        # print(state_data)
        # print(nation_data)
        # print(world_data)
        print('success')
        if len(patient_data) == 0:
            area = 'Your area has no data or no patients'
            patients = 0
        else:
            area=patient_data[0][2]
            patients = patient_data[0][3]
        # print()
        # print(patient_data[1])
        # patients = patient_data[0].to_json()
        # area = patient_data[1].to_json()
        all_data = {
            'No of patients in your area':patients,
            'Area name':area,
            'Your state name':state_data[1],
            'Total covid19 cases':state_data[2],
            'Total cured patients':state_data[3],
            'Total death':state_data[4],
            'In India total covid!9 cases': nation_data[0],
            'In India total patients cured': nation_data[1],
            'In India total deaths': nation_data[2],
            'World wide total covid19 active case':  world_data[0],
            'World wide total patients cured ': world_data[1],
            'World wide total covid19 death case': world_data[2],

            }
        # data = 'your area cases is '+patients
        # return JsonResponse(all_data,safe=False)
    #     data = {
    #     'name':'niranjan',
    #     'test': 'test output'
    # }
        return JsonResponse(all_data,safe= False)
        # return HttpResponse(data)

    else:
        main = {'status': False, 'msg': 'Username or password is not correct!'}
        return HttpResponse(json.dumps(main), content_type='application/json', status=401)
        # return HttpResponse('not post method')

    return HttpResponse('test')



def getPatientInformation(statename, city_name):
    URL = 'https://www.mohfw.gov.in/pdf/DistrictWiseList354.pdf'
    urllib.request.urlretrieve(URL, "docFiles/filename.pdf")

    f = DOCFILES_FOLDER+'filename.pdf'
    # print(f)

    convert_into(DOCFILES_FOLDER+'filename.pdf', 'docFiles/test.tsv', output_format='tsv', pages='all')
    rd = pd.read_csv(DOCFILES_FOLDER+'test.tsv', sep='\t', skiprows=2,
                     names=['state', 'no of dist affected', 'district', 'no of positive cases'])
    rd.ffill(axis=0, inplace=True)
    df = pd.DataFrame(rd)
    col1 = df.iloc[286:297, 1]
    col2 = df.iloc[286:297, 2]
    df.iloc[286:297, 1] = col2
    df.iloc[286:297, 2] = col1
    if type(statename) is str:
        state_info = df['state'] == statename.upper()
    else:
        state_info=' '
    mystate = df[state_info]
    for i in city_name:
        if type(i) is str:
            c = i.split()[0].upper()
            city = remove(c)
            # print(city)
            # valuee = mystate[mystate['district'].str.contains(city)]
            if mystate[mystate['district'].str.contains(city)].empty == False:
                valuee = mystate[mystate['district'].str.contains(city)]
                break

            else:
                valuee = pd.DataFrame()
                # valuee= valuee.append({'state':mystate,'no of dist affected':0,'district': city,'no of positive cases':0,}, ignore_index=True)
            # print(valuee)
            # print(mystate[mystate['district'].str.contains(city)])

        else:
            print(i)
    # print(valuee)


    # print(valuee)




            # valuee = mystate['district'].str.match(city)
            # valuee.dropna(inplace=True)

    # print(valuee)



    # no_of_cases = valuee['no of positive cases']
    # dist = valuee['district']
    # print(mystate[valuee])
    # print(df[state_info])
    # print('success')
    if os.path.exists(DOCFILES_FOLDER+'filename.pdf'):
        os.remove(DOCFILES_FOLDER+'filename.pdf')
    if os.path.exists(DOCFILES_FOLDER+'test.tsv'):
        os.remove(DOCFILES_FOLDER+'test.tsv')


    # my_list.append(no_of_cases)
    # my_list.append(dist)
    # print(valuee.values.tolist())
    return valuee.values.tolist()




def remove(string):
    pattern = re.compile(r'\s+')
    return re.sub(pattern, '', string)

def getNationData():
    url = 'https://www.mohfw.gov.in/'
    req_data = requests.get(url).text
    soup = BeautifulSoup(req_data, 'html.parser')
    target_div = soup.find('div', {'class': 'site-stats-count'})
    all_strong_tag = target_div.find_all('strong')
    data_lst = []
    for i in all_strong_tag:
        data_lst.append(i.text)
    active_case = data_lst[0]
    discharged = data_lst[1]
    death = data_lst[2]
    # print(active_case)
    # print(discharged)
    # print(death)
    nation_data = [active_case,discharged,death]
    return nation_data

def getStateData(statename):
    url = 'https://www.mohfw.gov.in/'
    req_data = requests.get(url).text
    soup = BeautifulSoup(req_data, 'html.parser')
    target_div2 = soup.find('div', {'class': 'data-table table-responsive'})
    # print(target_div2)
    table_data = target_div2.find_all('td')
    sl_no = []
    name_of_states = []
    active_patient = []
    recovered = []
    death = []

    # print(table_data)
    for i in range(0, len(table_data), 5):
        sl_no.append(table_data[i].text)
        if i < len(table_data)-10:
            # print(table_data[i+1].text)
            name_of_states.append(table_data[i + 1].text)
            active_patient.append(table_data[i + 2].text)
            recovered.append(table_data[i + 3].text)
            death.append(table_data[i + 4].text)
    all_data = zip(sl_no, name_of_states, active_patient, recovered, death)
    result = ''
    for i in all_data:
        if i[1] == statename:
            result = i
    print(result)
    return result

def getWorldWideData():
    url = 'https://www.worldometers.info/coronavirus/#countries'
    req_data = requests.get(url).text
    soup = BeautifulSoup(req_data, 'html.parser')
    case = soup.find_all('div', {'class': 'maincounter-number'})
    my_list =[]
    for i in case:
        my_list.append(i.find('span').text)
    # print(my_list)
    return my_list

@csrf_exempt
def test(request):
    data = {
        'name':'niranjan',
        'test': 'test output'
    }

    return JsonResponse(data,safe=False)
