import firebase_admin
from firebase_admin import credentials, firestore
import requests
from datetime import datetime

# ==========================================
# 1. CONEXIÓN A TU FIREBASE
# ==========================================
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("🚀 Conexión establecida con la nube de Firebase.")
except Exception as e:
    print(f"❌ Error al conectar: {e}")
    exit()

# ==========================================
# 2. FUNCIÓN PARA LIMPIAR DATOS VIEJOS
# ==========================================
def limpiar_eventos_viejos():
    """Borra todos los documentos de la colección 'eventos'"""
    print("🧹 Iniciando limpieza de eventos antiguos...")
    docs = db.collection('eventos').stream()
    contador = 0
    for doc in docs:
        doc.reference.delete()
        contador += 1
    print(f"✨ Limpieza terminada. Se borraron {contador} eventos.")

# ==========================================
# 3. FUNCIÓN PARA GUARDAR NUEVOS EVENTOS
# ==========================================
def guardar_evento_superticket(evento):
    """Procesa y guarda los datos corregidos"""
    try:
        # ID basado en el slug (nombre amigable)
        doc_id = f"st_{evento['slug']}"
        
        # Corrección de la URL de la imagen (sin doble /media/)
        path_imagen = evento['imagen_home']
        if path_imagen.startswith('/media/'):
            url_imagen = f"https://superticket.bo{path_imagen}"
        else:
            url_imagen = f"https://superticket.bo/media/{path_imagen}"
        
        # Limpieza final de barras
        url_imagen = url_imagen.replace("bo//", "bo/")

        datos = {
            'titulo': evento['nombre'],
            'fecha_hora': evento['desde_fecha'],
            'lugar': evento['lugar'],
            'ciudad': evento['lugar_responsive'],
            'precio_minimo': evento['entradas_online_desde'],
            'moneda': "Bs." if evento['moneda'] is None else evento['moneda'],
            'imagen': url_imagen,
            'url_compra': f"https://superticket.bo/evento/{evento['slug']}",
            'categoria': 'Evento Destacado',
            'fuente': 'SuperTicket.bo',
            'fecha_registro': datetime.now().strftime("%d/%m/%Y %H:%M")
        }

        db.collection('eventos').document(doc_id).set(datos)
        print(f"   📥 Guardado: {datos['titulo']}")
        
    except Exception as e:
        print(f"   ⚠️ Error procesando {evento.get('nombre')}: {e}")

# ==========================================
# 4. EJECUCIÓN PRINCIPAL
# ==========================================
def ejecutar_obrero_total():
    # Paso 1: Limpiar lo que ya hay
    limpiar_eventos_viejos()
    
    # Paso 2: Obtener lo nuevo
    print("\n🕵️ Obteniendo nuevos eventos desde SuperTicket...")
    url_api = "https://superticket.bo/obtener_eventos/?cantidad_eventos=100"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url_api, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            eventos_lista = data.get('eventos', [])
            
            print(f"📊 Se encontraron {len(eventos_lista)} eventos frescos.")
            for ev in eventos_lista:
                guardar_evento_superticket(ev)
                
            print(f"\n✅ TRABAJO TERMINADO. Tu base de datos está reluciente.")
        else:
            print(f"🚫 Error de servidor SuperTicket: {response.status_code}")

    except Exception as e:
        print(f"🚫 Error de conexión: {e}")

if __name__ == "__main__":
    ejecutar_obrero_total()