# MEMORIA DE TRABAJO - SmartInventory AI
## Fecha: 25 de Junio de 2026
## Estado: MÓDULOS COMPLETADOS - PENDIENTES MENORES

---

## RESUMEN DEL DIA

Se implementaron múltiples mejoras en el sistema: control de acceso por roles, selector de modelos IA, gráficos de predicción, predicción por categoría, módulo de modelos IA y documentación técnica.

### Logros principales
- Control de acceso por roles implementado.
- Selector de modelos IA (XGBoost/LightGBM) funcional.
- Gráficos de predicción con histórico de ventas.
- Predicción por categoría y multi-select de productos.
- Módulo de Modelos IA con gráficos comparativos.
- Documentación técnica de IA (página web).

---

## CAMBIOS REALIZADOS

### 1. Control de Acceso por Roles

| Archivo | Cambio |
|---------|--------|
| frontend/src/components/Layout.jsx | Menú filtrado por roles |
| frontend/src/components/RoleRoute.jsx | Nuevo componente de protección de rutas |
| frontend/src/App.jsx | Rutas protegidas según rol |

**Resultado:**
- Rol Vendedor (id=3): Solo ve Productos, Categorías, Proveedores, Inventario, Ventas.
- Rol Administrador (id=1) y Sistemas (id=2): Ven todos los módulos.

### 2. Selector de Modelos IA

| Archivo | Cambio |
|---------|--------|
| backend/app/schemas/prediccion.py | Agregado campo `id_modelo` opcional |
| backend/app/presentation/prediccion_routes.py | Endpoint acepta modelo seleccionado |
| frontend/src/pages/Prediccion.jsx | Selector de modelos + tabla comparativa |

**Resultado:**
- Usuario puede elegir entre XGBoost o LightGBM al generar predicciones.
- Tabla comparativa muestra métricas de ambos modelos.

### 3. Gráficos de Predicción

| Archivo | Cambio |
|---------|--------|
| backend/app/repositories/venta_repository.py | Método `get_sales_history_by_product()` |
| backend/app/presentation/venta_routes.py | Endpoint `GET /ventas/producto/{id}/historial` |
| frontend/src/pages/Prediccion.jsx | Gráficos con react-chartjs-2 |
| frontend/package.json | Instalado `react-chartjs-2` |

**Resultado:**
- Gráfico histórico de ventas (últimos 90 días).
- Gráfico de tendencia de demanda (predicciones).
- Intervalos de confianza visualizados (sombreado).
- Comparativa ventas reales vs predicción.

### 4. Predicción por Categoría

| Archivo | Cambio |
|---------|--------|
| backend/app/repositories/product_repository.py | Método `get_by_category()` |
| backend/app/presentation/product_routes.py | Endpoint `GET /products/categoria/{id}` |
| backend/app/schemas/prediccion.py | Schema `PrediccionBatchRequest` y `PrediccionBatchResponse` |
| backend/app/presentation/prediccion_routes.py | Endpoint `POST /predicciones/predecir-lote` |
| frontend/src/pages/Prediccion.jsx | Selector de categoría y multi-select |

**Resultado:**
- Predicción individual por producto.
- Predicción masiva por categoría (todos o selección).
- Barra de progreso durante predicción en lote.

### 5. Módulo de Modelos IA

| Archivo | Cambio |
|---------|--------|
| backend/app/models/modelos_ia.py | Agregado campo `r2` |
| backend/app/schemas/modelo_ia.py | Agregado campo `r2` |
| backend/app/repositories/modelo_ia_repository.py | Método `set_model_status()` |
| backend/app/presentation/modelo_ia_routes.py | Endpoints activar/desactivar |
| frontend/src/pages/ModelosIA.jsx | Página con gráficos comparativos |
| frontend/src/App.jsx | Ruta `/modelos-ia` |
| frontend/src/components/Layout.jsx | Menú "Modelos IA" |

**Resultado:**
- Tarjetas de cada modelo con métricas.
- Botón Activar/Desactivar por modelo.
- Gráfico comparativo de métricas.
- Tabla detallada con todas las métricas.

### 6. Documentación Técnica de IA

| Archivo | Cambio |
|---------|--------|
| DOCUMENTACION_IA/index.html | Página web completa de documentación |

**Resultado:**
- Introducción y objetivos.
- Fuente de datos (Dataset M5).
- Pipeline de ML documentado.
- Variables del modelo (28 features).
- Modelos explicados (XGBoost vs LightGBM).
- Métricas con fórmulas.
- Resultados y análisis.
- Arquitectura del sistema.
- Mejoras futuras.

### 7. Migraciones y Correcciones

| Archivo | Cambio |
|---------|--------|
| alembic/versions/a1b2c3d4e5f6_add_r2_to_modelos_ia.py | Migración para columna r2 |
| BD | Columna `r2` agregada a `modelos_ia` |
| BD | Valores R² actualizados (XGBoost: 0.722, LightGBM: 0.744) |

---

## ESTADO ACTUAL DEL PROYECTO

### Completado ✅
- Dashboard funcional.
- Gestión de productos, categorías, proveedores.
- Gestión de inventario.
- Gestión de ventas.
- Alertas básicas.
- Navegación mejorada.
- Base de datos definida.
- Flujo operativo funcional.
- Módulo de predicción integrado.
- Métricas de modelos (MAE, RMSE, R², MAPE).
- Selector de modelos IA (XGBoost/LightGBM).
- Control de acceso por roles.
- Gráficos de predicción con histórico de ventas.
- Predicción por categoría y multi-select de productos.
- Módulo de Modelos IA con gráficos comparativos.
- Documentación técnica de IA (página web).

### Pendiente 🔲
1. Exportación de reportes.
2. Dashboard analítico avanzado.
3. Validaciones robustas.
4. Alertas inteligentes avanzadas.
5. Preparación de documentación para sustentación.

---

## ARCHIVOS DE REFERENCIA

### TESIS
- Backend: `C:\Users\RRHH3\Desktop\VISUAL\TESIS\backend\`
- Frontend: `C:\Users\RRHH3\Desktop\VISUAL\TESIS\frontend\`
- ML Models: `C:\Users\RRHH3\Desktop\VISUAL\TESIS\backend\ml_models\`
- Documentación IA: `C:\Users\RRHH3\Desktop\VISUAL\TESIS\DOCUMENTACION_IA\`
- DB: MariaDB localhost:3307 / root:123456 / tesis_inventario

---

## NOTAS TECNICAS

### Roles del sistema
| ID | Nombre | Permisos |
|----|--------|----------|
| 1 | ADMINISTRADOR | Todos los permisos |
| 2 | SISTEMAS | Acceso técnico completo |
| 3 | VENTAS | Solo lectura + ventas |

### Modelos IA disponibles
| Modelo | R² | MAE | RMSE | MAPE | Archivo | Estado |
|--------|-----|-----|------|------|---------|--------|
| XGBoost | 0.722 | 1.658 | 3.650 | 70.25% | xgboost_model.pkl | ACTIVO |
| LightGBM | 0.744 | 1.658 | 3.502 | 70.80% | lightgbm_model.pkl | ACTIVO |

### Endpoints principales
```
POST /api/predicciones/predecir
POST /api/predicciones/predecir-lote
GET  /api/products?limit=2000
GET  /api/products/categoria/{id}
GET  /api/ventas/producto/{id}/historial?days=90
GET  /api/modelos-ia
PUT  /api/modelos-ia/{id}/activar
PUT  /api/modelos-ia/{id}/desactivar
```
