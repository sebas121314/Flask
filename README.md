# Hepatitis - API Flask con Regresion Logistica

Aplicacion Flask que expone un modelo de regresion logistica entrenado sobre el dataset de hepatitis (archivos `.pkl` ya incluidos). Se entrega una interfaz web ligera y una ruta JSON para integrar el modelo en otros sistemas.

## Requisitos

- Python 3.10 (se define en `runtime.txt` para Render)
- Pip

## Instalacion y ejecucion local

```bash
python -m venv .venv
.\.venv\Scripts\activate   # en Windows
pip install -r requirements.txt
python app.py
```

El servidor quedara en `http://127.0.0.1:5000/` con la pagina de formulario. Para usarlo en modo produccion local:

```bash
gunicorn app:app --bind 0.0.0.0:5000
```

## Uso del API

- `GET /health` comprueba estado.
- `POST /predict` recibe un JSON con los 21 campos enumerados en `archivos/modelo_regresion_logistica_info.json`.

Ejemplo:

```bash
curl -X POST http://127.0.0.1:5000/predict ^
  -H "Content-Type: application/json" ^
  -d "{\"Age\":45,\"Sex\":1,\"Estado_Civil\":1,\"Ciudad\":2,\"Steroid\":1,\"Antivirals\":2,\"Fatigue\":1,\"Malaise\":1,\"Anorexia\":2,\"Liver_Big\":1,\"Liver_Firm\":2,\"Spleen_Palpable\":2,\"Spiders\":2,\"Ascites\":2,\"Varices\":2,\"Bilirubin\":1.2,\"Alk_Phosphate\":85,\"Sgot\":45,\"Albumin\":4.0,\"Protime\":60,\"Histology\":1}"
```

El resultado incluye `prediction` (1=Fallece, 2=Sobrevive), probabilidad maxima y los valores enviados.

## Pruebas

```bash
pip install -r requirements-dev.txt
pytest
```

## Despliegue en Render

1) Haz fork o crea un repositorio nuevo en GitHub con estos archivos.  
2) En Render, crea un Web Service desde el repo.  
3) Usa `pip install -r requirements.txt` como build command y `gunicorn app:app --bind 0.0.0.0:$PORT` como start command (ya definido tambien en `render.yaml`).  
4) Render detecta `runtime.txt` para fijar Python 3.10.  
5) Cuando el deploy termine, Render mostrara la URL publica (entregable 1).

## Entregables solicitados

- URL Render: se obtiene tras completar el paso anterior.  
- URL GitHub: la del repo que crees con este codigo.  
- Printscreen de pruebas: puedes capturar la pagina principal (`/`) o la salida de `pytest`/`curl` mostrando prediction.
