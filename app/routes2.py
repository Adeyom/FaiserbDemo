from datetime import datetime
from flask import Blueprint, jsonify, render_template, render_template_string, request, redirect, url_for, flash
from flask_cors import CORS
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

@main.route('/connect', methods=['GET', 'POST'])
def connect():
    if request.method == 'POST':
        # Aquí manejarás la lógica del pago
        amount = request.form.get('amount')
        method = request.form.get('payment_method')
        flash(f"Pago de ${amount} con {method} procesado con éxito.", "success")
        return redirect(url_for('main.index'))
    return render_template('connect.html')

@main.route('/webhook3ds', methods=['GET','POST'])
def webhook3ds():
    if request.method == 'GET':
        return render_template('webhook3ds.html')
    else:
        print("POST")
        data = request.get_json()
        print("Received termURL data:", data)
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
                        "number": 4761120010000492, #dynamic_values.get('tarjeta',''),
                        "securityCode": 123, #dynamic_values.get('cvv',''),
                        "expiryDate": {
                            "month": 12, #month,
                            "year": 28 #year
                        }
                    }
                },
                "authenticationRequest": {
                    "authenticationType": "Secure3DAuthenticationRequest",
                    "termURL": "https://6db6-148-244-170-158.ngrok-free.app/webhook3ds",
                    "methodNotificationURL": "https://6db6-148-244-170-158.ngrok-free.app/webhook3ds",
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

        #         # Extraer contenido del iframe
        #         print(response_json)
        #         iframe_content = response_json.get('authenticationResponse', {}).get('secure3dMethod', {}).get('methodForm', '')
        #         ipgTransaction = response_json.get('ipgTransactionId', {})
        #         print("IPGTransaction: ",ipgTransaction)
        #         print("IFRAME: \n",iframe_content)
                
        #         if iframe_content:
        #             print("FIN")
        #             # Retornar una página HTML que incluya el iframe
        #             html_template = f"""
        #             <!DOCTYPE html>
        #             <html lang="en">
        #             <head>
        #                 <meta charset="UTF-8">
        #                 <meta name="viewport" content="width=device-width, initial-scale=1.0">
        #                 <title>Procesando Pago</title>
        #             </head>
        #             <body>
        #                 {iframe_content}
        #             </body>
        #             </html>
        #             """
        #             return render_template_string(html_template)
        #         else:
        #             return jsonify({"error": "No se encontró contenido del iframe en la respuesta"}), 500
        #     else:
        #         return jsonify({"error": f"Error en la solicitud: {response.status_code}", "details": response.text}), response.status_code

        # except requests.exceptions.RequestException as e:
        #     return jsonify({"error": f"Error al realizar la solicitud: {e}"}), 500
        
                try:
                    response_json = response.json()  # Intentar decodificar el JSON
                    print(response_json)
                    return jsonify({ # Retornar JSON al frontend
                        "transactionId": response_json.get("orderId", "N/A"),
                        "status": response_json.get("transactionStatus", "N/A"),
                        "amount": response_json.get("approvedAmount", {}).get("total", "N/A"),
                        "dateTime": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    }), 200
                    # return jsonify(response_json)  
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
