from datetime import datetime
import hashlib
import base64
import hmac

txndatetime = datetime.now().strftime("%Y:%m:%d-%H:%M:%S")
parametros= {
            "chargetotal": "25000.00",
            "txndatetime": txndatetime, 
            "currency": "484", 
            "responseFailURL": "https://pagosonline.mx/DConnect/response.php",
            "hash_algorithm": "HMACSHA256",
            "storename": "62130996",
            "timezone": "America/Mexico_City", 
            "responseSuccessURL": "https://pagosonline.mx/DConnect/response.php",
            "txntype":"sale",
            "checkoutoption": "combinedpage"
        }


cadena= parametros
key= "Alex2024$"

valores_ordenados = [cadena[clave] for clave in sorted(cadena)]
cadena_concatenada = "|".join(valores_ordenados)   
# Crear el hash HMAC-SHA256 usando la llave
hash_obj = hmac.new(key.encode(), cadena_concatenada.encode(), hashlib.sha256)
# Obtener el hash en formato hexadecimal
hash_hex = hash_obj.hexdigest()
# Convertir el hash hexadecimal a base64
hash_base64 = base64.b64encode(bytes.fromhex(hash_hex)).decode('utf-8')
print(cadena_concatenada ,hash_hex, hash_base64)



