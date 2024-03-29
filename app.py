from dotenv import load_dotenv
from flask import Flask,render_template,request,redirect,url_for
from flask_cors import CORS
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os,re,json
import base64
from modulation import *
from binascii import unhexlify
import logging


logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)

matplotlib.use('WebAgg')

load_dotenv()

app=Flask(__name__,static_url_path='/static')
CORS(app)


@app.template_filter('decode_hex')
def decode_hex(s):
    return unhexlify(s)


@app.template_filter('b64encode')
def b64encode(s):
    return base64.b64encode(s).decode('utf-8')

@app.route('/',methods=['GET'])
def home():
    f = open('./data.json')
    data = json.load(f)["Home"]
    return render_template('home.html',data=data)

@app.route('/references',methods=['GET'])
def references():
    return render_template('references.html')

@app.route('/theory/<modulation_type>',methods=["GET"])
def theory(modulation_type):
    return render_template(f'theory/{modulation_type}.html')

# ---------- Analog Modulation -------------------
@app.route('/AM',methods=['GET'])
def AM_page():
    f = open('./data.json')
    data = json.load(f)["AM"]
    return render_template('Analog_Modulation.html',data=data)

@app.route('/AM/<am_type>',methods=['GET','POST'])
def Amplitutde_Modulation(am_type):  
    
    title = {"MAIN":"Amplitutde Modulation","SSB":"SSB Modulation","DSBSC":"DSB Modulation","QAM":"QAM Modulation"}
    plots = []
    x_message = []
    x_carrier = []
    if (request.method=='POST'):
        content = request.form
        fm=int(content['fm'])
        fc=int(content['fc'])
        Am=int(content['Am'])
        Ac=int(content['Ac'])
        errMsg = ""
        message_signal = str(content['message_signal'])
        if(Am>Ac or fm>fc):
            errMsg = "The given plot is not possible. Because Fc <Fm or Ac<Am"
        inputs = {"Am":Am,"Ac":Ac,"fm":fm,"fc":fc,"message_signal":message_signal}
        
        if am_type == "MAIN":
            plots = AM_main_graph(inputs)
        elif am_type == "SSB":
            plots = AM_ssb_modulation(inputs)
        elif am_type == "DSBSC":
            inputs["phi"] = 1
            plots = AM_double_sideband_modulation(inputs)
        elif am_type == "QAM":
            message_signal_2 = request.form['message_signal_2']
            inputs["message_signal_2"] = message_signal_2
            plots = AM_QAM(inputs) 
        return render_template('AM_graphs.html',am_type=am_type.upper(),title=title[am_type],plots = plots,inputs=inputs,errMsg=errMsg)
    return render_template('AM_graphs.html',am_type=am_type.upper(),title=title[am_type],plots = plots)

@app.route('/FM/<index>',methods=['GET','POST'])
def FM(index):
    images = []
    index = int(index)
    inputs = {}
    errMsg = ""
    title={1:"Frequency modulation",2:"Phase modulation"}
    if request.method == 'POST':
        fm=int (request.form['fm'])
        fc=int (request.form['fc'])
        Am=int (request.form['Am'])
        Ac=int (request.form['Ac'])
        message_signal = str(request.form['message_signal'])
        K = int(request.form['K'])
        if(fc<fm or Ac<Am):
            errMsg = "Given graph is Not possible as Fc <Fm or Ac<Am." 
        inputs = {"Am":Am,"Ac":Ac,"fm":fm,"fc":fc,"message_signal":message_signal,"K":K}
        x = np.linspace(-200,200,10000) #domain for the modulated_wave
        s = [1 for i in x]
        if(index==1):
            images = FM_MAIN(x,inputs)           
        elif(index==2):
            images = PHASE_MAIN(x,inputs) 
      
    return render_template('fm_graphs.html',title=title[index],index=index,plots=images,inputs=inputs,errMsg=errMsg)

# ---------- End of Analog Modulation ------------


# ---------- Digital Modulation ---------------------

@app.route('/DM',methods=['GET'])
def DM_page():
    f = open('./data.json')
    data = json.load(f)["DM"]
    return render_template('Digital_Modulation.html',data=data)


@app.route('/DM/<dmtype>', methods=['GET','POST'])
def DigitalModulation(dmtype):
    title = {"BPSK":"BPSK Modulation","BFSK":"BFSK Modulation","BASK":"BASK Modulation","QPSK":"QPSK Modulation"}
    plots = []
    inputs = {}

    if (request.method=='POST'):
      Tb=float (request.form['Tb'])
      fc=int (request.form['fc'])
      binaryInput = str(request.form['inputBinarySeq'])
      inputs = {"Tb":Tb,"fc":fc,"binaryInput":binaryInput}
      fc2=1
      if(dmtype=='BFSK'):
          fc2=int (request.form['fc2'])

      # Change Binary string to array
      inputBinarySeq = np.array(list(binaryInput), dtype=int)

      if dmtype.upper() == 'BASK':
          plots = BASK(Tb, fc, inputBinarySeq)
      elif dmtype.upper() == 'BFSK':
          plots = BFSK(Tb, fc, fc2, inputBinarySeq)
      elif dmtype.upper() == 'BPSK':
          plots = BPSK(Tb, fc, inputBinarySeq)
      elif dmtype.upper() == 'QPSK':
          plots = QPSK(Tb, fc, inputBinarySeq)
    return render_template('DM_graphs.html',dmtype=dmtype.upper(),title=title[dmtype], plots=plots,inputs=inputs)

@app.route('/DM2/<dmtype>', methods=['GET','POST'])
def GMSK_Modulation(dmtype):
    title = {"GMSK":"GMSK Modulation"}
    plots = []
    inputs = {}
    if (request.method=='POST'):
        a= str (request.form['data_stream'])
        fc= int (request.form['fc'])
        osmp_factor= int (request.form['osmp_factor'])
        bt_prod= float (request.form['bt_prod'])

        inputs = {"a":a,"fc":fc,"omsp_factor":osmp_factor,"bt_prod":bt_prod}
        if dmtype.upper() == 'GMSK':
            plots = GMSK(a, fc, osmp_factor, bt_prod)
    
    return render_template('GMSK_graphs.html',dmtype=dmtype.upper(),title=title[dmtype], plots=plots,inputs=inputs)    


@app.route('/DM3/<dmtype>', methods=['GET','POST'])
def DPSK_Modulation(dmtype):
    title = {"DPSK":"DPSK Modulation"}
    plots = []
    inputs = {}
    if (request.method=='POST'):
        fm= int (request.form['fm'])
        Am= int (request.form['am'])
        phi_m= int (request.form['phi_m'])
        fc= int (request.form['fc'])
        Ac= int (request.form['ac'])
        phi_c= int (request.form['phi_c'])
        inputs = {'fm':fm,'Am':Am,'phi_m':phi_m,'phi_c':phi_c}
        if dmtype.upper() == 'DPSK':
            plots = DPSK(fm, Am, phi_m, fc, Ac, phi_c)
    return render_template('DPSK_graphs.html',dmtype=dmtype.upper(),title=title[dmtype], plots=plots,inputs=inputs)    


# ------------ End of Digital Modulation -------------

# ------------ COMPUTER NETWORKS ---------------------

@app.route('/CN',methods=["GET"])
def CN_page():
    f = open('./data.json')
    data = json.load(f)["CN"]
    return render_template('home.html',title="COMPUTER NETWORKS",data=data)

@app.route('/CN/<algo_type>',methods=["GET"])
def CN_algo_page(algo_type):
    return render_template(f'CN/{camelCase(algo_type)}.html',title=algo_type,include_files=[f'css/{algo_type}.css',f'js/{algo_type}.js'])

# ------------ End of Computer Networks --------------



# ---------- Pulse Modulation ---------------------

# @app.route('/PM',methods=['GET'])
# def PM_page():
#     f = open('./data.json')
#     data = json.load(f)["PM"]
#     return render_template('Pulse_Modulation.html',data=data)


# @app.route('/PM/<pmtype>', methods=['GET','POST'])
# def PulseModulation(pmtype):
#     title = {"Sampling":"Sampling",
#              "Quantization":"Quantization",
#              "PAM":"Pulse Amplitude Modulation",
#              "PPM":"Pulse Phase Modulation",
#              "PCM":"Pulse Position Modulation",
#              "PWM":"Pulse Width Modulation"
#              }
#     plots = []
#     inputs = []
#     print(request.form)
#     if (request.method=='POST'):
#         fm = int (request.form['fm'])
#         am = int (request.form['am'])
#         fc = int (request.form['fc'])
#         ac = int (request.form['ac'])
#         message_type = str(request.form["message_signal"])
#         inputs = [am,ac,fm,fc,message_type]

#       # Change Binary string to array
#         print(pmtype)
#         if pmtype.upper() == 'PPM':
#             ppm_ratio = float(request.form['ppm_ratio'])        
#             inputs.append(ppm_ratio)
#             plots = PPM(inputs)
#         elif pmtype.upper() == 'PAM':
#           inputs.append(int(request.form['fs']))
#           plots = PAM(inputs)
#         elif pmtype.upper() == 'BPSK':
#           plots = BPSK(Tb, fc, inputBinarySeq)
#         elif pmtype.upper() == 'QPSK':
#           plots = QPSK(Tb, fc, inputBinarySeq)

#     return render_template('PM_graphs.html',pmtype=pmtype.upper(),title=title[pmtype], plots=plots)

def camelCase(sentence):
    sentence = re.sub(r'[^a-zA-Z0-9 ]', '', sentence)
    words = sentence.split()
    camel_cased_words = [words[0].lower()] + [word.capitalize() if i == 0 else word.lower() for i, word in enumerate(words[1:])]
    camel_cased_sentence = ''.join(camel_cased_words)    
    return camel_cased_sentence

def create_app():
    PORT = int(os.environ.get("PORT",8000))
    app.run(host='0.0.0.0',port=PORT)

if __name__ == "__main__":
    create_app()