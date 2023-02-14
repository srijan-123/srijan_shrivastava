import requests

def get_flights_data(source,destination,date):

    del_list=['delhi','Delhi','del','DELHI']
    bel_list=['bangalore','ben']

    if source in del_list:
        source='New Delhi'
    
    if destination in del_list:
        destination="New Delhi"
    
    if source in bel_list:
        source='Bengaluru'
    
    if destination in bel_list:
        destination="Bengaluru"

    url="https://script.googleusercontent.com/macros/echo?user_content_key=p5SdSCeqVSQaegH2dC9HIuKQot6Ofs6oXVIEJFFyoX6-Hn0FwtifRhiUEyWZzsZpU4t28r0o6_2gBz_v69IMEncVErba3B8rOJmA1Yb3SEsKFZqtv3DaNYcMrmhZHmUMWojr9NvTBuBLhyHCd5hHa4NzdQtol61jBqwhAgn1cWO7myaShnyjWXZ_koJc_Ds0mwH75lAzZEPOCE7s_7yoL6kwlOrUxD1Iw81hxj3JzG2H9ZNf8jIYDwXIuFltvcj9ZlfCfEzpIpdH01AEmWbRaQ&lib=MFsd9etQbKyEYzj2fdAUkRI_UZ19k2LD0"
    response=requests.get(url)
    data=response.json()
    result=[]
    for i in data:
        if i['Source']==source.title() and i['Destination']==destination.title() and i['Date'].split('T')[0]==date:
            result.append([i["Date"].split('T')[0],(i["ArrivalTime"].split('T')[1]).split('.')[0],(i["Departure Time"].split('T')[1]).split('.')[0],i["Flight "],i["Source"],i["Destination"],i["Price"],i["Day of Week"],i["Month"]])
    
    if len(result)>1:
        result=result[0]
    
    return result