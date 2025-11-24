# Guía Completa de Ejecución y Funcionamiento del Proyecto Hepatitis - Flask con Regresión Logística

Esta guía explica detalladamente cómo configurar, ejecutar, probar y desplegar la aplicación Flask que implementa un modelo de regresión logística para predecir resultados de hepatitis en pacientes. La aplicación carga un modelo pre-entrenado y proporciona tanto una interfaz web como una API REST para realizar predicciones.

## Descripción General del Proyecto

El proyecto es una aplicación web construida con **Flask** que utiliza un modelo de **regresión logística** para predecir si un paciente con hepatitis "fallecerá" (clase 1) o "sobrevivirá" (clase 2) basándose en 21 características médicas. El modelo fue entrenado con un conjunto de datos de hepatitis y alcanza una precisión perfecta (1.0) en los sets de entrenamiento y prueba, aunque esto puede indicar sobreajuste en producción si no se ajusta el modelo con datos nuevos.

### Componentes Principales
- **app.py**: Aplicación Flask principal con rutas para la interfaz web, API y salud del sistema.
- **archivos/modelo_regresion_logistica.pkl**: Modelo de regresión logística serializado.
- **archivos/scaler.pkl**: Escalador de características (StandardScaler de scikit-learn).
- **archivos/modelo_regresion_logistica_info.json**: Metadatos del modelo (features, métricas, etc.).
- **requirements.txt**: Dependencias principales.
- **requirements-dev.txt**: Dependencias adicionales para pruebas.
- **runtime.txt**: Versión de Python requerida (3.10.15).
- **render.yaml**: Configuración de despliegue para Render.
- **tests/test_app.py**: Pruebas automatizadas.

### Funcionamiento Técnico
1. **Carga de Artefactos**: Al iniciar, carga el modelo, escalador y metadatos desde archivos pickle/JSON.
2. **Escalado de Características**: Aplica transformación StandardScaler a las entradas numéricas.
3. **Predicción**: Usa el modelo para predecir probabilidades y clases.
4. **API REST**: Endpoints GET/POST para salud y predicción.
5. **Interfaz Web**: Página HTML con formulario para input manual y visualización de resultados.

## Prerrequisitos

Para ejecutar este proyecto necesitas:
- **Python 3.10.15** (especificado en `runtime.txt`, compatible con plataformas como Render).
- **Pip** (instalado por defecto con Python).
- Conexión a internet para instalar paquetes.

El proyecto funciona en Windows (como en tu sistema), Linux y macOS.

## Instalación y Configuración Local

### 1. Clonación/Descarga del Proyecto
Si no tienes el código:
- Clona desde GitHub: `git clone <URL_DEL_REPO>` (si el proyecto está en GitHub).
- O descárgalo como ZIP y extráelo.

El directorio de trabajo debe ser la carpeta raíz del proyecto (donde está `app.py`).

### 2. Configuración del Entorno Virtual
Se recomienda usar un entorno virtual para aislar dependencias:

```bash
# Crear entorno virtual (Windows)
python -m venv .venv

# Activar entorno virtual (Windows)
.\.venv\Scripts\activate

# Verificar que Python está en el entorno
python --version  # Debe mostrar Python 3.10.x
```

### 3. Instalación de Dependencias
Instala los paquetes requeridos:

```bash
pip install -r requirements.txt
```

Esto instala:
- **Flask 3.0.3**: Framework web para Python.
- **gunicorn 23.0.0**: Servidor WSGI para producción.
- **joblib 1.4.2**: Para cargar modelos pickle.
- **numpy 1.26.4**: Computación numérica.
- **scikit-learn 1.6.1**: Para el modelo ML.
- **scipy 1.13.1**: Dependencia de scikit-learn.

## Ejecución en Modo Desarrollo

En modo desarrollo, Flask inicia un servidor local con recarga automática para cambios en el código.

```bash
# Asegúrate de que el entorno virtual esté activado
python app.py
```

### Qué Sucede:
- El servidor arranca en `http://127.0.0.1:5000/` (localhost:5000).
- Abre `http://127.0.0.1:5000/` en tu navegador para ver la interfaz web.
- El modo debug está activado, mostrando errores detallados en la consola.
- Los cambios en `app.py` recargarán automáticamente el servidor.

### Interfaz Web
- **Título**: "Predicción de Hepatitis" con nombre del modelo.
- **Formulario**: Campos numéricos para las 21 características (ej: Age, Sex, Bilirubin).
- **Ayuda Contextual**: Popover explica valores binarios (1=Sí/No para síntomas).
- **Botón Predecir**: Envía POST a `/predict` y muestra resultados JSON en `<pre>`.
- **Resultado**: Incluye predicción (1=Fallece, 2=Sobrevive), probabilidad máxima, inputs validados y metadatos del modelo.

### Endpoints disponibles:
- `GET /`: Página principal con formulario HTML.
- `GET /health`: Retorna `{"status": "ok"}` para verificar salud.
- `POST /predict`: API para predicción (ver más abajo).

## Ejecución en Modo Producción Local

Para simular un entorno de producción local:

```bash
gunicorn app:app --bind 0.0.0.0:5000
```

### Diferencias con Desarrollo:
- **gunicorn**: Servidor WSGI multi-proceso más apropiado para producción.
- **Sin debug**: Errores no se muestran en navegador, solo logs en consola.
- **Múltiples Trabajadores**: Puede manejar más peticiones concurrentes.
- **Puerto 0.0.0.0**: Accesible desde cualquier IP si necesitas probar externamente.

## Uso del API REST

La aplicación expone una API JSON para integración con otros sistemas.

### Endpoint Health
```bash
curl GET http://127.0.0.1:5000/health
```

Respuesta esperada:
```json
{
  "status": "ok"
}
```

Útil para monitoreo de uptime.

### Endpoint Predicción
```bash
curl -X POST http://127.0.0.1:5000/predict ^
  -H "Content-Type: application/json" ^
  -d "{\"Age\":45,\"Sex\":1,\"Estado_Civil\":1,\"Ciudad\":2,\"Steroid\":1,\"Antivirals\":2,\"Fatigue\":1,\"Malaise\":1,\"Anorexia\":2,\"Liver_Big\":1,\"Liver_Firm\":2,\"Spleen_Palpable\":2,\"Spiders\":2,\"Ascites\":2,\"Varices\":2,\"Bilirubin\":1.2,\"Alk_Phosphate\":85,\"Sgot\":45,\"Albumin\":4.0,\"Protime\":60,\"Histology\":1}"
```

#### Campos Requeridos (Todas las 21 características deben incluirse):
- **Demográficos**: Age (edad numérica), Sex (1=masculino, 2=femenino), Estado_Civil (codificación numérica del dataset original), Ciudad (codificación numérica).
- **Síntomas Binarios** (1=Sí/No): Steroid, Antivirals, Fatigue, Malaise, Anorexia, Liver_Big, Liver_Firm, Spleen_Palpable, Spiders, Ascites, Varices, Histology.
- **Pruebas de Sangre Numéricas**: Bilirubin, Alk_Phosphate, Sgot, Albumin, Protime.

#### Respuesta Exitosa (200):
```json
{
  "prediction": 2,
  "label": "Sobrevive",
  "probability": 0.95,  // Probabilidad máxima de la clase predicha
  "inputs": {            // Valores numéricos validados enviados
    "Age": 45.0,
    ...
  },
  "model_meta": {        // Info del modelo usado
    "modelo": "Regresión Logística",
    "n_features": 21
  }
}
```

#### Errores Comunes:
- **400**: Campos faltantes (ej: "Faltan campos: Age, Sex").
- **400**: Valores inválidos (cobertura de errores para conversiones fallidas).
- **500**: Errores internos (registro en logs, respuesta genérica al cliente).

### Integración con la Interfaz Web
- El formulario HTML envía JSON idéntico a la API.
- JavaScript captura la respuesta y la muestra formateada como JSON.
- Errores se exhiben en el elemento `<pre>`.

## Pruebas Automatizadas

Para ejecutar las pruebas con pytest:

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Ejecutar pruebas
python -m pytest
# o directamente: pytest
```

### Pruebas Incluidas:
- **test_health_endpoint**: Verifica que `/health` retorne status 200 y `ok`.
- **test_predict_endpoint_accepts_payload**: Envía payload de muestra y verifica:
  - Status 200
  - Presencia de "prediction" y "inputs" en respuesta
  - Valores de input correctos

Si pasan, indica que la aplicación carga correctamente modelos y procesa predicciones.

## Despliegue en Producción (Render)

### Preparación
1. **Crea Repo GitHub**: Sube todo el código a un repositorio público en GitHub.
2. **Configura Render**: Crea cuenta en https://render.com y conecta tu repo.

### Pasos en Render
1. En panel de control > "New" > "Web Service".
2. Selecciona repo, elije plan Free.
3. Build & Deployment:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - Runtime se detecta automáticamente desde `runtime.txt` (Python 3.10).
4. Deploy: Render construye y muestra URL pública (ej: https://hepatitis-flask.onrender.com).

### Archivo render.yaml
El `render.yaml` define la configuración:
- Tipo: `web`
- Ambiente: `python`
- Plan: `free` (gratuito con límites)
- Comandos ya especificados.

### Consideraciones de Producción
- **Uptime Limitado**: Planes Free duermen sin tráfico.
- **SSL**: Render proporciona HTTPS automáticamente.
- **Logs**: Accede via dashboard para debugging.
- **Variables ENV**: No usadas aquí, pero disponibles para configuración avanzada.

## Flujo Completo de Procesamiento

1. **Inicio App**: Carga modelo, scaler y features desde archivos.
2. **Validación Input**: Convierte a float, checa campos obligatorios.
3. **Escalado**: Aplica StandardScaler (media=0, varianza=1 para normalización).
4. **Predicción**: Modelo de regresión logística (función sigmoide) genera probabilidades.
5. **Output**: Clase predicha (argmax), prob max y metadatos.

## Troubleshooting Común

- **Error Import**: Asegúrate de activar entorno virtual: `.\.venv\Scripts\activate`.
- **Puerto Ocupado**: Cambia puerto en `app.run(port=5001)`.
- **Falta Dependencia**: `pip install -r requirements.txt`.
- **Modelo No Found**: Verifica archivos en `archivos/` estén presentes.
- **Pruebas Fallback**: Errores pueden no mostrar detalles si no es modo debug.

## Extenciones y Mejoras Sugeridas

- Reentrenar modelo con más datos para reducir sobreajuste.
- Añadir validación input más robusta.
- Implementar autenticación API.
- Agregar logging persistente (no solo consola).
- Usar Docker para contenerización.

Esta guía cubre completamente setup, ejecución y funcionamiento. Para cualquier duda, revisa logs de consola o archivos de código.
