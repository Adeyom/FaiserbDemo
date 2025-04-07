from datetime import datetime
from flask import Blueprint, app, jsonify, render_template, render_template_string, request, redirect, url_for, flash
import base64
import hashlib
import hmac
import json
import uuid
import requests
import time


main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/response' , methods=['GET'])
def response():
    return render_template('response.html')

@main.route('/respuesta_pago', methods=['POST'])
def respuesta_pago():
    datos_respuesta = request.form.to_dict()  # Convierte la respuesta en un diccionario
    # Verificar si la transacción fue aprobada
    estado_transaccion = datos_respuesta.get("approval_code")
    ccbin= datos_respuesta.get("ccbin")
    cardnumber= datos_respuesta.get("cardnumber")
    card = ccbin + cardnumber[7:]

    es_aprobada= True if estado_transaccion[0] == "Y" else False

    return render_template('respuesta_pago.html', datos=datos_respuesta, es_aprobada=es_aprobada, card=card)


@main.route('/connect_iframe', methods=['GET', 'POST'])
def connectIframe():
    if request.method == 'GET':
        return render_template('connect_iframe.html')
    else:
        try:
            print("Entrando en el POST")
            datos = request.json
            print("Datos recibidos:", datos)
            productos = datos.get("productos", [])
            if not productos:
                return jsonify({"mensaje": "El carrito está vacío"}), 400
            
            
            total = str(sum(producto["precio"] for producto in productos))
            txndatetime = datetime.now().strftime("%Y:%m:%d-%H:%M:%S")

            parametros = {
                "chargetotal": total,
                "txndatetime": txndatetime, 
                "currency": "484", 
                "responseFailURL": "https://c390-148-244-170-158.ngrok-free.app/respuesta_pago",
                "hash_algorithm": "HMACSHA256",
                "storename": "62130996",
                "timezone": "America/Mexico_City", 
                "responseSuccessURL": "https://c390-148-244-170-158.ngrok-free.app/respuesta_pago",
                "txntype": "sale",
                "checkoutoption": "combinedpage",
                "parentUri": "https://c390-148-244-170-158.ngrok-free.app/connect_iframe"
            }

            key = "Alex2024$"
            valores_ordenados = [parametros[clave] for clave in sorted(parametros)]
            cadena_concatenada = "|".join(valores_ordenados)

            # Crear el hash HMAC-SHA256
            hash_obj = hmac.new(key.encode(), cadena_concatenada.encode(), hashlib.sha256)
            hash_hex = hash_obj.hexdigest()
            hash_base64 = base64.b64encode(bytes.fromhex(hash_hex)).decode('utf-8')

            print("Envio exitoso\n","Hash extended:", hash_base64, "\n","Total: ", total,"\n", "Fecha y hora: ",txndatetime)
            return jsonify({
                "cadena_concatenada": cadena_concatenada,
                "hash_hex": hash_hex,
                "hash_base64": hash_base64,
                "total": total,
                "txndatetime": txndatetime
            }), 200
            

        except Exception as e:
            print("Error en el servidor:", str(e))
            return jsonify({"error": "Error interno del servidor"}), 500


@main.route('/connect1', methods=['GET', 'POST'])
def connect():
    if request.method == 'GET':
        return render_template('connect1.html')
    else:
        try:
            print("Entrando en el POST")
            datos = request.json
            print("Datos recibidos:", datos)
            productos = datos.get("productos", [])
            if not productos:
                return jsonify({"mensaje": "El carrito está vacío"}), 400
            
            
            total = str(sum(producto["precio"] for producto in productos))
            txndatetime = datetime.now().strftime("%Y:%m:%d-%H:%M:%S")

            parametros = {
                "chargetotal": total,
                "txndatetime": txndatetime, 
                "currency": "484", 
                "responseFailURL": "http://127.0.0.1:5000/respuesta_pago",
                "hash_algorithm": "HMACSHA256",
                "storename": "62130996",
                "timezone": "America/Mexico_City", 
                "responseSuccessURL": "http://127.0.0.1:5000/respuesta_pago",
                "txntype": "sale",
                "checkoutoption": "combinedpage",
            }

            key = "Alex2024$"
            valores_ordenados = [parametros[clave] for clave in sorted(parametros)]
            cadena_concatenada = "|".join(valores_ordenados)

            # Crear el hash HMAC-SHA256
            hash_obj = hmac.new(key.encode(), cadena_concatenada.encode(), hashlib.sha256)
            hash_hex = hash_obj.hexdigest()
            hash_base64 = base64.b64encode(bytes.fromhex(hash_hex)).decode('utf-8')

            print("Envio exitoso\n","Hash extended:", hash_base64, "\n","Total: ", total,"\n", "Fecha y hora: ",txndatetime)
            return jsonify({
                "cadena_concatenada": cadena_concatenada,
                "hash_hex": hash_hex,
                "hash_base64": hash_base64,
                "total": total,
                "txndatetime": txndatetime
            }), 200
            

        except Exception as e:
            print("Error en el servidor:", str(e))
            return jsonify({"error": "Error interno del servidor"}), 500


@main.route('/webhook3ds', methods=['GET','POST'])
def webhook3ds():
    if request.method == 'GET':
        return render_template('webhook3ds.html')
    else:
        print("POST")
        # Obtén los datos del formulario enviados mediante POST
        threeDSMethodData = request.form['threeDSMethodData']  # Convierte los datos del formulario en un diccionario
        print("ThreeDSMethodData:", threeDSMethodData)
        
        # Procesa la respuesta del flujo 3D Secure
        return jsonify({"status": "success"}), 200

@main.route('/api', methods=['GET', 'POST'])
def api():
    
    url = "https://.api.firstdata.com/gateway/v2" #URL base, define ambiente prod o test.
    content = None

    if request.method == 'POST':
        data = request.get_json()  # Recibir datos como JSON desde el frontend
        print("Datos recibidos del frontend:", data)
        #Manejo de Ambientes
        # Capturamos el valor seleccionado del radio button
        environment = data.get('environment')
    
        # Validamos el valor seleccionado
        if environment == "prod":
            result = url[:8] + environment + url[8:] 
            print("Resultado", result)

        elif environment == "cert":
            result = url[:8] + environment + url[8:] 
            print("Resultado", result)
        else:
            result = "No seleccionaste ningún ambiente."

        

        # Llaves de API 
        apiKey = data.get('apiKey')
        apiSecret = data.get('apiSecret')
        
        # Definir el contenido basado en la opción seleccionada
        selected_option = data.get('option')
        # selected_option = "1"
        if selected_option == "1":
            content = "/payments"
        elif selected_option == "2":
            content = "Contenido para la operación Token."
        elif selected_option == "3":
            content = "Contenido para Devolución/Cancelación."
        elif selected_option == "4":
            content = "Contenido para PaymentURL."
        elif selected_option == "5":
            content = "Contenido para Información."
        elif selected_option == "6":
            content = "Contenido para Programado."
        elif selected_option == "7":
            content = "Contenido para Personalizado."
        else:
            content = "Seleccione una opción válida."
        print("contenido", content)

        # Payload dinámico
        dynamic_values = {key: value for key, value in data.items() if key not in ['environment', 'apiKey', 'apiSecret', 'option']}
        print("Valores dinámicos:", dynamic_values)

        # Ejemplo de validación de tarjeta (puedes ajustar)
        try:
            expiry_date = dynamic_values.get('expiracion', '')  # Formato esperado: MM/YY
            print("Fecha de expiración: ",expiry_date)
            if '/' in expiry_date:
                month, year = map(int, expiry_date.split('/'))
            else:
                month, year = None, None
        except ValueError:
            return jsonify({"error": "Fecha de expiración inválida"}), 400


        #-----Armar y enviar petición-----
        # Construcción de la URL base
        finalUrl = result + content
        print(finalUrl)
        print(month)
        print(year)

        total = dynamic_values.get('charge','')

        # Construcción del payload
        payloadSale = {
            "transactionAmount": {
                    "total": 500,
                    "currency": "MXN" #dynamic_values.get('currency','')
                },
                "requestType": "PaymentCardSaleTransaction",
                "paymentMethod": {
                    "paymentCard": {
                        "number": 4265880000000007, #dynamic_values.get('tarjeta',''),
                        "securityCode": 123, #dynamic_values.get('cvv',''),
                        "expiryDate": {
                            "month": 12, #month,
                            "year": 28 #year
                        }
                    }
                },
                "authenticationRequest": {
                    "authenticationType": "Secure3DAuthenticationRequest",
                    "termURL": "https://42b6-148-244-170-158.ngrok-free.app/webhook3ds",
                    "methodNotificationURL": "https://42b6-148-244-170-158.ngrok-free.app/webhook3ds",
                    "challengeIndicator": "01"
    }
        }



        print(payloadSale)



        # Generación de ID único
        clientRequestId = str(uuid.uuid4())

        # Tiempo en formato EPOCH (milisegundos)
        epoch_time_milliseconds = str(int(time.time() * 1000))

        # Creación del mensaje para la firma (convertimos el payload a JSON)
        payloadSale_json = json.dumps(payloadSale)  # Convertir el payload a una cadena JSON
        message = f"{apiKey}{clientRequestId}{epoch_time_milliseconds}{payloadSale_json}"

        # Generación de la firma HMAC
        signature = hmac.new(apiSecret.encode(), message.encode(), hashlib.sha256).digest()
        b64_sig = base64.b64encode(signature).decode()

        # Configuración de los headers
        headers = {
            "Content-Type": "application/json",
            "Client-Request-Id": clientRequestId,
            "Api-key": apiKey,
            "Timestamp": epoch_time_milliseconds,
            "Message-Signature": b64_sig
        }

        try:
            response = requests.post(finalUrl, json=payloadSale, headers=headers)
            if response.status_code == 200:
                response_json = response.json()        
                try:
                    response_json = response.json()  # Intentar decodificar el JSON
                    print("\n\n\nRESPONSE:\n" + str(response_json), "\n\n")
                    iframe_content = response_json.get('authenticationResponse', {}).get('secure3dMethod', {}).get('methodForm', '')
                    ipgTransaction = response_json.get('ipgTransactionId', {})
                    print("IPGTransaction: \n" + ipgTransaction, "\n\n")
                    print("IFRAME: \n" + iframe_content, "\n\n")

                    return jsonify({ # Retornar JSON al frontend
                        "transactionId": response_json.get("orderId", "N/A"),
                        "status": response_json.get("transactionStatus", "N/A"),
                        "amount": response_json.get("approvedAmount", {}).get("total", "N/A"),
                        "dateTime": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    }), 200

                except json.JSONDecodeError:
                    return jsonify({"error": "Respuesta no contiene un JSON válido"}), 500
            else:
                response_json = response.json()  # Intentar decodificar el JSON
                print(response_json)
                return jsonify({"error": f"Error en la solicitud: Código de estado {response.status_code}", "details": response.text}), response.status_code

        except requests.exceptions.RequestException as e:
            print(f"Error al realizar la solicitud: {e}")
            return render_template('api.html', error="Error al realizar la solicitud.")

    else:
        return render_template('api.html')
    

    
@main.route('/api/content', methods=['GET'])
def api_content():
    selected_option = request.args.get('option')
    if selected_option == "1":
        content = '''
        <h4>PAYMENT SETUP</h4>
        <div class="row gy-3">
        <!-- Columna de dropdown y charge total -->
        <div class="col-md-6">
            <!-- Dropdown para monedas -->
            <div class="mb-3">
                <label for="currency" class="form-label">Moneda</label>
                <select class="form-select" id="currency" name="currency">
                    <option value="MXN">MXN</option>
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                </select>
            </div>
            <!-- Input para charge total -->
            <div class="mb-3">
                <label for="chargeTotal" class="form-label">Charge Total</label>
                <input type="text" class="form-control" id="chargeTotal" name="charge" placeholder="$0.00">
            </div>
        </div>
        <div class="col-md-6 d-flex flex-column">
            <div class="form-check">
                <input class="form-check-input" type="checkbox" id="3ds" name="3ds">
                <label class="form-check-label" for="3ds">3DS</label>
            </div>
            <div class="form-check">
                <input class="form-check-input" type="checkbox" id="mit" name="mit">
                <label class="form-check-label" for="mit">MIT</label>
            </div>
            <div class="form-check">
                <input class="form-check-input" type="checkbox" id="preauth" name="preauth">
                <label class="form-check-label" for="preauth" >Preauth</label>
            </div>
            <div class="form-check">
                <input class="form-check-input" type="checkbox" id="msi" name="installments">
                <label class="form-check-label" for="msi" >Installments</label>
            </div>
        </div>
        <hr class="my-4">
        <h4>PAYMENT</h4>
        <div class="row gy-3">
            <div class="col-md-6">
              <label for="cc-name" class="form-label">Name on card</label>
              <input type="text" class="form-control" id="cc-name" name="nombre" placeholder="" required="">
              <small class="text-body-secondary">Full name as displayed on card</small>
              <div class="invalid-feedback">
                Name on card is required
              </div>
            </div>

            <div class="col-md-6">
              <label for="cc-number" class="form-label">Credit card number</label>
              <input type="text" class="form-control" id="cc-number" name="tarjeta" placeholder="" required="">
              <div class="invalid-feedback">
                Credit card number is required
              </div>
            </div>

            <div class="col-md-3">
              <label for="cc-expiration" class="form-label">Expiration</label>
              <input type="text" class="form-control" id="cc-expiration" name="expiracion" placeholder="" required="">
              <div class="invalid-feedback">
                Expiration date required
              </div>
            </div>

            <div class="col-md-3">
              <label for="cc-cvv" class="form-label">CVV</label>
              <input type="text" class="form-control" id="cc-cvv" name="cvv" placeholder="" required="">
              <div class="invalid-feedback">
                Security code required
              </div>
            </div>
        </div>

        '''
    elif selected_option == "2":
        content = '''
        <div class="col-md-6">
              <label for="cc-number" class="form-label">Credit card number</label>
              <input type="text" class="form-control" id="cc-number" name="token" placeholder="" required="">
              <div class="invalid-feedback">
                Credit card number is required
              </div>
            </div>
        '''
    elif selected_option == "3":
        content = "<p><strong>Operación:</strong> Devolución/Cancelación. Pasos para procesar devoluciones o cancelaciones.</p>"
    elif selected_option == "4":
        content = "<p><strong>Operación:</strong> PaymentURL. Detalles sobre cómo generar un PaymentURL.</p>"
    elif selected_option == "5":
        content = "<p><strong>Operación:</strong> Información. Aquí encontrarás datos relevantes.</p>"
    elif selected_option == "6":
        content = "<p><strong>Operación:</strong> Programado. Información sobre operaciones programadas.</p>"
    elif selected_option == "7":
        content = "<p><strong>Operación:</strong> Personalizado. Personaliza tu operación según tus necesidades.</p>"
    else:
        content = "<p>Seleccione una opción válida.</p>"

    return content, 200
