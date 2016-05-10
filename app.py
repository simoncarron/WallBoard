import config as CONFIG
import xml.etree.ElementTree as ET
import time
import thread



import requests
from flask import Flask, render_template,jsonify
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

huntListArray = []

url="https://"+CONFIG.CUCM_HOSTNAME+":8443/perfmonservice/services/PerfmonPort?wsdl"

headers = {'content-type': 'text/xml','SOAPAction' : 'CUCM:DB ver=10.5'}

body = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:soap="http://schemas.cisco.com/ast/soap">
   <soapenv:Header/>
   <soapenv:Body>
      <soap:perfmonCollectCounterData>
         <soap:Host>"""+CONFIG.CUCM_HOSTNAME+"""</soap:Host>
         <soap:Object>Cisco Hunt Lists</soap:Object>
      </soap:perfmonCollectCounterData>
   </soapenv:Body>
</soapenv:Envelope>"""

def getDataFromCUCM(threadName):
    while True:
        del huntListArray[:]
        response = requests.post(url,data=body,headers=headers,verify=False,auth=HTTPBasicAuth(CONFIG.CUCM_USERNAME, CONFIG.CUCM_PASSWORD))
        root = ET.fromstring(response.text)

        for item in root[0][0][0].findall('item'):
            if CONFIG.HUNTLIST_SELECT in item.find('Name').text:

                huntList = {}
                huntList['Name']=item.find('Name').text
                huntList['Value']=item.find('Value').text
                huntListArray.append(huntList)

        time.sleep(CONFIG.PULLING_TO_CUCM)
        print "%s: %s" % ( threadName, time.ctime(time.time()) )

try:
  thread.start_new_thread( getDataFromCUCM, ("Thread-1", ) )
except:
   print "Error: unable to start thread"


@app.route("/HuntList")
def huntList():
    return jsonify(results=huntListArray)

@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(
        host='0.0.0.0'
    )