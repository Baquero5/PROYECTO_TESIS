# MEMORIA DE TRABAJO - SmartInventory AI
## Fecha: 1 de Julio de 2026
## Estado: RE-ENTRENAMIENTO EN PROCESO

---

## RESUMEN DEL DIA

Se inició el re-entrenamiento completo del modelo predictivo. Se corrigieron los scripts de entrenamiento para usar las mismas 19 features del backend (compatibilidad total). Se optimizó el script 03 para manejar el volumen de datos (9.5M filas) sin problemas de memoria.

---

## LOGROS PRINCIPALES

### 1. Corrección de Scripts de Entrenamiento
- **Script 01**: Corregido bug de `kagglehub` (argumento `competition_id`)
- **Script 03**: Reescrito para:
  - Agregar features faltantes: `is_holiday`, `month_sin`, `dayofweek_sin`, `rolling_max_28`, `rolling_min_28`
  - Usar `float32` en vez de `float64` (reduce memoria 50%)
  - Guardar CSV por chunks para evitar OOM
  - Eliminar export `m5_con_features.csv` (innecesario)
- **Scripts 05, 06, 07, 08**: FEATURE_COLS actualizado a 19 variables del backend

### 2. Features del Modelo Unificadas (19 variables)
Las mismas en entrenamiento y backend:
- Calendario: `dayofweek`, `month`, `is_month_end`
- Lags: `lag_1`, `lag_7`, `lag_14`, `lag_28`
- Rolling: `rolling_mean_7/14/28`, `rolling_std_7/28`, `rolling_max_28`, `rolling_min_28`
- Precio: `price`, `price_change_1`
- Temporalidad: `is_holiday`, `month_sin`, `dayofweek_sin`

### 3. Base de Datos Repoblada
- Script 04 ejecutado: 1000 productos, 9551 ventas, 5.4M detalles
- 3 categorías (Alimentos, Hogar, Deportes)
- 5 proveedores registrados

---

## PROCESO DE RE-ENTRENAMIENTO

### Scripts ejecutados hasta ahora

| # | Script | Estado | Descripcion |
|---|--------|--------|-------------|
| 01 | `01_descargar_m5.py` | ✅ | Descarga dataset M5 |
| 02 | `02_transformar_m5.py` | ✅ | Transforma ancho → largo |
| 03 | `03_features.py` | ⏳ | Feature engineering (pendiente re-ejecutar) |
| 04 | `04_poblar_bd.py` | ✅ | Pobla MariaDB |
| 05 | `05_entrenar_xgboost.py` | ⏳ | Pendiente re-ejecutar |
| 06 | `06_entrenar_lightgbm.py` | ⏳ | Pendiente re-ejecutar |
| 07 | `07_evaluar_modelos.py` | ⏳ | Pendiente re-ejecutar |
| 08 | `08_predecir.py` | ⏳ | Opcional |
| 09 | `09_registrar_modelos_bd.py` | ⏳ | Pendiente |

### Orden de ejecución restante

```bash
cd C:\Users\RRHH3\Desktop\VISUAL\TESIS\ml_training\src

# Paso 1: Generar dataset con 19 features correctas
python 03_features.py

# Paso 2: Repoblar BD
python 04_poblar_bd.py

# Paso 3: Entrenar modelos
python 05_entrenar_xgboost.py
python 06_entrenar_lightgbm.py

# Paso 4: Evaluar
python 07_evaluar_modelos.py

# Paso 5: Registrar en BD
python 09_registrar_modelos_bd.py
```

### Después de entrenar: Copiar modelos al backend

```bash
copy C:\Users\RRHH3\Desktop\VISUAL\TESIS\ml_training\models\xgboost_model.pkl C:\Users\RRHH3\Desktop\VISUAL\TESIS\backend\ml_models\
copy C:\Users\RRHH3\Desktop\VISUAL\TESIS\ml_training\models\lightgbm_model.pkl C:\Users\RRHH3\Desktop\VISUAL\TESIS\backend\ml_models\
```

### Reiniciar backend

```bash
cd C:\Users\RRHH3\Desktop\VISUAL\TESIS\backend
uvicorn app.main:app --reload --port 8000
```

---

## BUGS CORREGIDOS HOY

### 1. kagglehub API (script 01)
- **Error**: `competition_download() got an unexpected keyword argument 'competition_id'`
- **Solución**: Llamada sin keyword arguments

### 2. Features inconsistentes (scripts 03-08)
- **Error**: Modelo entrenado con 27 features, backend esperaba 19
- **Solución**: Unificar a 19 features del backend en todos los scripts

### 3. Out of Memory (script 03)
- **Error**: `Unable to allocate 1.14 GiB` al procesar 9.5M filas
- **Solución**: Usar `float32`, guardar por chunks, eliminar columnas innecesarias

---

## ESTADO ACTUAL DEL PROYECTO

### Completado ✅
- Dashboard analítico avanzado (7 KPIs, 6 gráficos, 3 tablas)
- Gestión de productos, categorías, proveedores
- Gestión de inventario con movimientos
- Gestión de ventas con detalle multi-item
- Alertas inteligentes con detección automática
- Sistema de notificaciones (NotificationBell)
- Módulo de predicción individual y por lote
- Selector de modelos IA con activar/desactivar
- Control de acceso por roles (33 permisos)
- Exportación de reportes (CSV, Excel, PDF)
- Documentación técnica de IA (página web)
- Corrección de 7 bugs críticos
- Protección JWT completa en todos los endpoints
- Migración a httpOnly cookies seguras
- Corrección del motor de predicción (ensemble + festivos Ecuador)
- Scripts de entrenamiento movidos a TESIS/ml_training/
- **Features unificadas: 19 variables en entrenamiento y backend**
- **Script 03 optimizado para manejar 9.5M filas**

### En Proceso ⏳
1. **RE-ENTRENAMIENTO DEL MODELO** (scripts 03-09 pendientes de re-ejecutar)
2. Copiar modelos a backend/ml_models/
3. Reiniciar backend y verificar predicciones

### Pendiente 🔲
1. Documentación para sustentación
   - Diagrama ER actualizado
   - Casos de uso
   - Flujo del negocio

---

## ARCHIVOS DE REFERENCIA

### TESIS
- Backend: `C:\Users\RRHH3\Desktop\VISUAL\TESIS\backend\`
- Frontend: `C:\Users\RRHH3\Desktop\VISUAL\TESIS\frontend\`
- ML Training: `C:\Users\RRHH3\Desktop\VISUAL\TESIS\ml_training\`
- ML Models (backend): `C:\Users\RRHH3\Desktop\VISUAL\TESIS\backend\ml_models\`
- Documentación IA: `C:\Users\RRHH3\Desktop\VISUAL\TESIS\DOCUMENTACION_IA\`
- DB: MariaDB localhost:3307 / root:123456 / tesis_inventario

### ENTRENAMIENTO (REFERENCIA - NO MODIFICAR)
- Scripts originales: `C:\Users\RRHH3\Desktop\VISUAL\ENTRENAMIENTO\src\`
- Metrics: `C:\Users\RRHH3\Desktop\VISUAL\ENTRENAMIENTO\metrics\`
- Models: `C:\Users\RRHH3\Desktop\VISUAL\ENTRENAMIENTO\models\`

---

## NOTAS TECNICAS

### Roles del sistema
| ID | Nombre | Permisos |
|----|--------|----------|
| 1 | ADMINISTRADOR | Todos los permisos (38) |
| 2 | SISTEMAS | Acceso técnico (28 permisos) |
| 3 | VENTAS | Solo lectura + ventas (10 permisos) |

### Features del Modelo (19 variables - Backend y Entrenamiento)
```python
FEATURE_COLS = [
    "price", "dayofweek", "month", "is_month_end",
    "lag_1", "lag_7", "lag_14", "lag_28",
    "rolling_mean_7", "rolling_mean_14", "rolling_mean_28",
    "rolling_std_7", "rolling_std_28",
    "price_change_1",
    "is_holiday", "month_sin", "dayofweek_sin",
    "rolling_max_28", "rolling_min_28",
]
```

### Festivos Ecuador (Dinámicos)
- Fijos: Año Nuevo, Día del Trabajo, Batalla de Pichincha, Independencia de Guayaquil, Primer Grito de Independencia, Día de los Difuntos, Independencia de Cuenca, Navidad
- Móviles: Carnaval (lunes y martes), Viernes Santo (calculados por algoritmo de Pascua)

### Backend ml_service.py - Métodos principales
| Método | Descripción |
|--------|-------------|
| `load_model()` | Carga modelo .pkl desde disco |
| `load_ensemble()` | Carga ensemble XGBoost + LightGBM |
| `get_feature_columns()` | Retorna 19 features del modelo |
| `get_v2_feature_columns()` | Alias de get_feature_columns() |
| `add_v2_features()` | Agrega features v2 a dataframe |
| `prepare_features_from_history()` | Prepara features desde historial de ventas |
| `predict_demand()` | Genera predicciones con ensemble o individual |

### Endpoints principales (todos protegidos)
```
POST /api/auth/login              (público)
POST /api/auth/logout             (autenticado)
GET  /api/auth/me                 (autenticado)
POST /api/predicciones/predecir   (PREDICCION_IA_LEER)
POST /api/predicciones/predecir-lote (PREDICCION_IA_LEER)
GET  /api/products                (PRODUCTOS_LEER)
GET  /api/products/categoria/{id} (PRODUCTOS_LEER)
GET  /api/ventas/producto/{id}/historial?days=90 (VENTAS_LEER)
GET  /api/modelos-ia              (PREDICCION_IA_LEER)
PUT  /api/modelos-ia/{id}/activar (CONFIGURACION_ACTUALIZAR)
PUT  /api/modelos-ia/{id}/desactivar (CONFIGURACION_ACTUALIZAR)
```

### Credenciales
- Email: admin@sistema.com
- Contraseña: Admin123!

---

## PARA CONTINUAR (PROXIMO PASO)

### Ejecutar en orden:
```bash
cd C:\Users\RRHH3\Desktop\VISUAL\TESIS\ml_training\src
python 03_features.py
python 04_poblar_bd.py
python 05_entrenar_xgboost.py
python 06_entrenar_lightgbm.py
python 07_evaluar_modelos.py
python 09_registrar_modelos_bd.py
```

### Copiar modelos y reiniciar backend:
```bash
copy ..\models\xgboost_model.pkl ..\..\backend\ml_models\
copy ..\models\lightgbm_model.pkl ..\..\backend\ml_models\
cd ..\..\backend
uvicorn app.main:app --reload --port 8000
```
