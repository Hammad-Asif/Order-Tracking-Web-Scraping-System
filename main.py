from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup
import json
import traceback
import re
from datetime import datetime
from pyairtable import Table
from pyairtable.formulas import match
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from datetime import datetime, timedelta
app = Flask(__name__)
CORS(app)
# Configure logging settings
app.logger.setLevel(logging.DEBUG)

# Create a file handler to write logs to a file
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)

# Define the log format
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(log_format)

# Add the file handler to the logger
app.logger.addHandler(file_handler)
class scrapeForm():
    def __init__(self):
        self.url = "http://xep-cloud.innovapty.com:8090/TrackingPage.aspx"

        # Send a GET request to retrieve the initial page
        response = requests.get(self.url)

        # Parse the HTML content of the page
        self.soup = BeautifulSoup(response.text, "html.parser")

        # Find the input element and extract its name and value
        input_element = self.soup.find("input", {"name": "_strNumber"})
        self.input_name = input_element["name"]
        # Prepare the form data with the user input
        self.appLog=app.logger
        self.appLog.info("Class Object Declared")
    def addInAIrtable(self,result):
        try:
            self.appLog.info("Adding Tracking Record to Airtable")
            table=Table("keyU3gbAZs5xrultB","appoF4IOrZPSS4qAi","tblBX1M7P1kQMPVpm")
            
            data={"Tracking":result['Tracking #'],
                            "Received Date":result["Received Date"],
                            "Last Update":result["Last update"],
                            "Manifiest":result["Manifiest"],
                            "Status":result["Status"]
                            }
            if "Country" in result.keys():
                data["Country"]=result["Country"]
            if "Current Location" in result.keys():
                data["Current Location"]=result["Current Location"]
            tb=table.create(data)
            self.appLog.info("Tracking Record Added to Airtable")
        except Exception as e:
            app.logger.error("Failed to Add : %s", traceback.format_exc())
            app.logger.error(e)
            

    def Mail(self,tracking_number,val):
        try:
            table=Table("","appoF4IOrZPSS4qAi","tblUh8pgt2Vdfxmam")
            formula=match({"Tracking":tracking_number})
            airtable=table.all(formula=formula)
            if airtable['response']=='' or (airtable['response']=='Received' and datetime.now()-airtable['created']>=timedelta(days=2)):
                self.SendMail(tracking_number,val)
        except Exception as e:
            app.logger.error("Failed to Add response: %s", traceback.format_exc())
            return traceback.format_exc()
    def add_recordInAirtable(self,tracking_number):
        try:
            table=Table("keyU3gbAZs5xrultB","appoF4IOrZPSS4qAi","tblUh8pgt2Vdfxmam")
            # tracking='keyU3gbAZs5xr'
            mails=','.join(['desconocidos@nelconcargo.com', 'trafficmia@nelconcargo.com','warehouse@nelconcargo.com'] + ['jake.harris@tradexxcorp.com','kira@nelconcargo.com','hperez@nelconcargo.com'])
            tb=table.create({'Tracking#':tracking_number,'Email Sent':mails})
            self.appLog.info("Email Record Added to Airtable")
        except Exception as e:
            app.logger.error("Failed to Add response: %s", traceback.format_exc())
            return traceback.format_exc()
    def SendMail(self,Tracking,Manifiest):
        sender = 'traffic@tradexxcorp.com'
        receivers = ['desconocidos@nelconcargo.com', 'trafficmia@nelconcargo.com','warehouse@nelconcargo.com']
        cc=['jake.harris@tradexxcorp.com','kira@nelconcargo.com','hperez@nelconcargo.com']

        meniSubject = 'Recuperación urgente del número de seguimiento:'+Tracking
        ManifiestEmail='''Estimado equipo de Nelcon,

Espero que este mensaje les encuentre bien.

Me pongo en contacto con ustedes debido a un paquete con el tracking: {{}}, al parecer, fue asignado erróneamente a otro agente. Solicitamos cordialmente que se revise este incidente y se realice la correspondiente reasignación del paquete para que pueda ser enviado adecuadamente a la cuenta de Tradexx.

Nuestro sistema estará monitoreando la situación cada 24 horas. En caso de que no se efectúe la corrección, recibirán otro correo de seguimiento. Sin embargo, una vez que el paquete haya sido reasignado y enviado correctamente, cesarán las notificaciones referentes a este asunto. Favor colocar la actualizacion en sistema con asignacion a Tradexx para que el sistema pueda validar correctamente cuando se realizo el cambio y la recuperación del paquete.

Agradecemos de antemano su atención y colaboración en este tema. Estamos seguros de que con su ayuda se resolverá a la mayor brevedad.

Saludos cordiales,

Tradexx

Nota: Este es un mensaje automatizado.'''.format(Tracking)
        otherSubject='Solicitud de apoyo con número de tracking - Asignación a cuenta TradExx'
        otherMAil='''<p>Estimado equipo de Nelcon Cargo,
Espero que estén teniendo un excelente día. Me dirijo a ustedes para solicitar su apoyo con respecto al número de seguimiento: {}, el cual ha quedado registrado como desconocido. Les agradecería que lo asignen a la cuenta de TradExx. En caso de que el envío tenga un peso superior a 20 lb, les solicito que me envíen un correo electrónico para evaluar la posibilidad de asignarlo por vía aérea, ya que no tengo acceso a la información de peso desde mi plataforma. Sin embargo, si el peso es inferior a esa cifra, les agradecería que realicen el envío por vía aérea en el próximo vuelo de salida, con el fin de evitar retrasos en la entrega al cliente.  Agradezco de antemano su apoyo y colaboración en este asunto.

Favor notar que este es un mensaje automático de nuestro sistema de correos, por favor confirmar la recepción de este correo con la palabra "recibido" para evitar que se reenvíe automáticamente el mensaje gracias.

Saludos cordiales,

TradExx Corp</p>'''.format(Tracking)
        try:
            
            message = MIMEMultipart()
            message["From"] = sender
            message["To"] = ', '.join(receivers)
            message["Cc"] = ', '.join(cc)
            if Manifiest:
                message["Subject"] =meniSubject
                message.attach(MIMEText(ManifiestEmail, "html")) 
            else:
                message["Subject"] =otherSubject
                message.attach(MIMEText(otherMAil, "html")) 

            # Add the body to the message
            

            # Create a secure SSL context
            context = ssl.create_default_context()

            # Connect to the SMTP server
            with smtplib.SMTP_SSL("smtp.stackmail.com", 465, context=context) as server:
                # Login to the sender's email
                server.login(sender, "Tradexx6804.")
                all_recipients = receivers + cc
                # Send the email
                server.sendmail(sender, all_recipients, message.as_string())
                self.appLog.info("Email sent")
                self.add_recordInAirtable()
        except Exception as e:
            print("Error:",e)
            self.appLog.error("Email Sent failed, Error: %s", str(e))
    def getQuickCourier(self,tracking_number):
        tracking_number1 = re.findall(r'[a-zA-Z0-9]+', tracking_number)
        tracking_number1=''.join(tracking_number1)
        # Prepare the form data with the user input
        try:
            
            form_data = {
                self.input_name: tracking_number1,
                "__EVENTTARGET": "",
                "__EVENTARGUMENT": "",
                "__VIEWSTATE": self.soup.find("input", {"name": "__VIEWSTATE"})["value"],
                "__VIEWSTATEGENERATOR": self.soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"],
                "__EVENTVALIDATION": self.soup.find("input", {"name": "__EVENTVALIDATION"})["value"],
                "__ASYNCPOST": "true",
                "btnQuickCourier": "Submit",
                # "btnWarehouse":"Submit"
            }

            # Send a POST request with the form data
            response = requests.post(self.url, data=form_data)

            # Parse the HTML content of the response
            soup = BeautifulSoup(response.text, "html.parser")
            if soup.find("span",{"id": "ErrorLabel"})==None:
            # Extract the result data or any other required information from the response
                result_element = soup.find("span", {"id": "lblTKResult"})
                result = result_element.text if result_element else ""
                # print("result is:",result,len(result),len(result)!=0,"No records matching" not in result)
                self.appLog.info("line# 172")
                self.appLog.info("result type is:",type(result_element))
                self.appLog.info("result is:",result_element)
                if "No records matching" not in result and len(result)!=0:
                    soup = BeautifulSoup(str(result_element), 'html.parser')
                    row_divs = soup.find_all('div', class_='row')

                    keys = [cell.text.strip() for cell in row_divs[0].find_all('div')]
                    values = [cell.text.strip() for cell in row_divs[1].find_all('div')]
                    keys=[x if x!='Batch' else "Received Date" for x in keys]
                    result = dict(zip(keys, values))
                    self.appLog.info("Result found on web with tracking Number %s",result['Tracking #'])
                    digits = re.findall(r'\d+', result['Manifiest'])
                    digits=''.join(digits)
                    digits=digits[0:min(len(digits),8)]
                    date=datetime.strptime(digits, '%Y%m%d').date()
                    date = date.strftime('%m/%d/%y')
                    table=Table("keyU3gbAZs5xrultB","appoF4IOrZPSS4qAi","tblCrezHKd4l4QOe9")
                    formula=match({"Tracking":result['Tracking #']})
                    airtable=table.all(formula=formula)
                    if airtable !=[]:
                        airtable=airtable[0]['fields']
                        date=datetime.strptime(airtable['Last Modified'], "%Y-%m-%dT%H:%M:%S.%fZ").date()
                        date = date.strftime("%m/%d/%Y")
                        result['Last update']=date
                        self.appLog.info("Result found on Airtable with tracking Number %s",tracking_number)
                    else:
                        formula=match({"Tracking":tracking_number})
                        airtable=table.all(formula=formula)
                        if airtable !=[]:
                            airtable=airtable[0]['fields']
                            date=datetime.strptime(airtable['Last Modified'], "%Y-%m-%dT%H:%M:%S.%fZ").date()
                            date = date.strftime("%m/%d/%Y")
                            result['Last update']=date
                            self.appLog.info("Result found on Airtable with tracking Number %s",tracking_number)

                        else:
                            result['Last update']=date

                    if result['Manifiest']=='':
                        result['Status']="Pending"
                    elif 'XEP' in result['Manifiest']:
                        result['Status']="In Transit to next facilty"
                        result['Country']="United States"
                    elif 't' in result['Manifiest'].lower() and 'd' in result['Manifiest'].lower() and 'x' in result['Manifiest'].lower(): #if tdx or tradexx is in there
                        if airtable!=[]:
                            print(airtable.keys())
                        else:
                            print('airtable is empty')
                        if airtable!=[] and 'Branch' in airtable.keys():
                            result['Status']="Arrived to "+airtable['Branch']
                            result['Current Location']=airtable['Branch']
                            result['Country']="Panama"
                        else:
                            result['Status']="Arrived to Panama"
                            result['Current Location']="Panama"
                            result['Country']="Panama"
                    else:
                        if airtable!=[] and (airtable['Branch'] =='Panama' or airtable['Branch'] =='Boquete'): 
                            result['Country']="United States"
                            result['Current Location']=airtable['Branch']

                        if airtable!=[] and airtable['Branch'] !='Panama' and airtable['Status']=="Ready for pickup":
                            result['Status']='ready to pickup'
                            result['Current Location']=airtable['Branch']

                        elif airtable!=[] and airtable['Status']=='Delivered':
                            result['Status']='Deliberate'
                            if 'Signed By' in airtable.keys():
                                result['Signed By']=airtable['Signed By']
                        else:
                            result['Status']="Delayed"
                            # self.SendMail(tracking_number,True)
                    self.appLog.info("Final Result: %s",str(result))
                    
                            
                    # if result['Manifiest']=='':
                    #     result['Status']="Pending"
                    # elif 'XEP' in result['Manifiest']:
                    #     result['Status']="In Transit to Panama"
                    # elif 't' in result['Manifiest'].lower() and 'd' in result['Manifiest'].lower() and 'x' in result['Manifiest'].lower():
                    #     result['Status']="Arrived at Panama"
                    # else:
                    #     result['Status']="Delayed"
                    
                    # for warehouse data
                    form_data = {
                        self.input_name: tracking_number,
                        "__EVENTTARGET": "",
                        "__EVENTARGUMENT": "",
                        "__VIEWSTATE": self.soup.find("input", {"name": "__VIEWSTATE"})["value"],
                        "__VIEWSTATEGENERATOR": self.soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"],
                        "__EVENTVALIDATION": self.soup.find("input", {"name": "__EVENTVALIDATION"})["value"],
                        "__ASYNCPOST": "true",
                        # "btnQuickCourier": "Submit",
                        "btnWarehouse":"Submit"
                    }

                    # Send a POST request with the form data
                    response = requests.post(self.url, data=form_data)

                    # Parse the HTML content of the response
                    soup = BeautifulSoup(response.text, "html.parser")

                    # Extract the result data or any other required information from the response
                    consignee_line = soup.find('span', id='lblTKResult')
                    try:
                        # consignee_line=consignee_line.find(text='Consignee:')
                        
                        if 'Consignee:' in consignee_line.text:
                            if "DESCONO".lower() in consignee_line.text.lower():
                                result['Unknown']="Yes"
                                self.appLog.info("DESCONO found in warehouse data")
                                # self.SendMail(tracking_number,False)
                            else:
                                result['Unknown']="No"
                                self.appLog.info("DESCONO not found in warehouse data")

                        else:
                            result['Unknown']="No"
                            self.appLog.info("Consignee not found in warehouse data")

                            # result['Unknown']=consignee_line

                    except Exception as e:
                        result['Unknown']="No"
                        result['Unknown']=e
                    json_output = json.dumps(result)
                    self.addInAIrtable(result)
                    return json_output
                else:
                    self.appLog.info("Result not found on web with tracking Number %s",tracking_number)
                    table=Table("keyU3gbAZs5xrultB","appoF4IOrZPSS4qAi","tblCrezHKd4l4QOe9")
                    formula=match({"Tracking":tracking_number})
                    airtable=table.all(formula=formula)
                    result={}
                    result['Tracking #']=tracking_number
                    if airtable !=[]:
                        airtable=airtable[0]['fields']
                        date=datetime.strptime(airtable['Last Modified'], "%Y-%m-%dT%H:%M:%S.%fZ").date()
                        date = date.strftime("%m/%d/%Y")
                        result['Last update']=date
                        if  'Branch' in airtable.keys():
                            result['Status']="Arrived to "+airtable['Branch']
                            result['Country']="Panama"
                        else:
                            result['Status']="Arrived to Panama"
                            result['Country']="Panama"
                        
                        if 'Branch' in airtable.keys() and (airtable['Branch'] =='Panama' or airtable['Branch'] =='Boquete'): 
                            result['Country']="United States"
                        if 'Branch' in airtable.keys() and airtable['Branch'] !='Panama' and airtable['Status']=="Ready for pickup":
                            result['Status']='ready to pickup'
                        elif 'Status' in airtable.keys() and airtable['Status']=='Delivered':
                            result['Status']='Deliberate'
                            if 'Signed By' in airtable.keys():
                                result['Signed By']=airtable['Signed By']
                        
                        self.appLog.info("Final Result from Airtable: %s",str(result))
                        
                                
                        # if result['Manifiest']=='':
                        #     result['Status']="Pending"
                        # elif 'XEP' in result['Manifiest']:
                        #     result['Status']="In Transit to Panama"
                        # elif 't' in result['Manifiest'].lower() and 'd' in result['Manifiest'].lower() and 'x' in result['Manifiest'].lower():
                        #     result['Status']="Arrived at Panama"
                        # else:
                        #     result['Status']="Delayed"
                        
                # for warehouse data
                        form_data = {
                            self.input_name: tracking_number,
                            "__EVENTTARGET": "",
                            "__EVENTARGUMENT": "",
                            "__VIEWSTATE": self.soup.find("input", {"name": "__VIEWSTATE"})["value"],
                            "__VIEWSTATEGENERATOR": self.soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"],
                            "__EVENTVALIDATION": self.soup.find("input", {"name": "__EVENTVALIDATION"})["value"],
                            "__ASYNCPOST": "true",
                            # "btnQuickCourier": "Submit",
                            "btnWarehouse":"Submit"
                        }

                        # Send a POST request with the form data
                        response = requests.post(self.url, data=form_data)

                        # Parse the HTML content of the response
                        soup = BeautifulSoup(response.text, "html.parser")

                        # Extract the result data or any other required information from the response
                        consignee_line = soup.find('span', id='lblTKResult')
                        try:
                            consignee_line=consignee_line.find(text='Consignee:')
                            
                            if consignee_line:
                                if not (('t' in consignee_line.lower() and 'd' in consignee_line.lower() and 'x' in consignee_line.lower()) or 'xep' in consignee_line.lower()):
                                    self.appLog.info("TRADEX or TRADEXX or TDX or TDXX or XEP not found in warehouse data")
                                    # self.SendMail(tracking_number,False)
                                elif ('t' in consignee_line.lower() and 'd' in consignee_line.lower() and 'x' in consignee_line.lower()) :
                                    result['Status']="Waiting For Confirmation"
                                    self.appLog.info("TRADEX or TRADEXX or TDX or TDXX found in warehouse data")
                                elif "DESCONO".lower() in consignee_line.lower():
                                    result['Status']="Delayed"
                                    result['Unknown']="Yes"
                                    self.appLog.info("DESCONO found in warehouse data")
                                    # self.SendMail(tracking_number,False)
                                else:
                                    result['Status']="Delayed"
                                    result['Unknown']="No"
                                    self.appLog.info("DESCONO not found in warehouse data")

                            else:
                                self.appLog.info("TRADEX or TRADEXX or TDX or TDXX or DESCONO not found in warehouse data")
                                result['Status']="ALert for package not received"
                                result['Unknown']="No"
                        except:
                            result['Status']="ALert for package not received"
                            self.appLog.info("TRADEX or TRADEXX or TDX or TDXX or DESCONO not found in warehouse data")
                            result['Unknown']="No"
                            self.appLog.info("Consignee not found in warehouse data")

                        json_output = json.dumps(result)
                        self.addInAIrtable(result)
                        return json_output
                    json_output = json.dumps({'error':"No result found"})
                    return json_output
            else:
                app.logger.error("Error is : The warehouse database is down")
                json_output = json.dumps({'error2':'The warehouse database is down'})
                return json_output
        except Exception as e:
                app.logger.error("Error in scraping: %s, Error is : %s",str(e), traceback.format_exc())
                json_output = json.dumps({'error':str(e)})
                return json_output
    
@app.route('/QuickCourier', methods=['POST'])
def track_package():
    try:
        tracking_number = request.form.get('tracking_number')
        form=scrapeForm()
        return form.getQuickCourier(tracking_number)
    except Exception as e:
        app.logger.error("Failed to scrape: %s", traceback.format_exc())
        return traceback.format_exc()
@app.route('/response', methods=['POST'])
def mail_response():
    try:
        id = request.form.get('id')
        table=Table("keyU3gbAZs5xrultB","appoF4IOrZPSS4qAi","tblUh8pgt2Vdfxmam")
        table.update(id,{'response':'Received'})
        return "Your reponse has been received"
    except Exception as e:
        app.logger.error("Failed to Add response: %s", traceback.format_exc())
        return traceback.format_exc()

@app.route("/", methods=["GET"])
def tracking_page():
    # return "hello world"
    return render_template("template.html")

if __name__ == '__main__':
    # app.run(debug=True)
    app.run()
else:
    application = app