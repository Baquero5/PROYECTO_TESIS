# Pendientes Identificados del Proyecto SmartInventory AI

## 1. Gráficos de Predicción
**Estado:** Completado ✅

### Implementado
- Gráfico histórico de ventas (últimos 90 días).
- Gráfico de tendencia de demanda (predicciones).
- Intervalos de confianza visualizados (sombreado).
- Comparativa ventas reales vs predicción.
- Selector de horizonte (7, 14, 30, 60 días).
- Tooltip interactivo con información detallada.

### Beneficio
Permite interpretar visualmente los resultados del modelo predictivo.

---

## 2. Métricas del Modelo Predictivo
**Estado:** Completado ✅

### Implementado
- MAE (Mean Absolute Error).
- RMSE (Root Mean Squared Error).
- MAPE (Mean Absolute Percentage Error).
- R² (Coeficiente de Determinación).
- Tabla comparativa de modelos en frontend.

### Beneficio
Permite validar científicamente la calidad de las predicciones.

---

## 3. Explicación Técnica de la Inteligencia Artificial
**Estado:** Pendiente

### Documentar
- Algoritmo utilizado.
- Variables de entrada.
- Variables de salida.
- Proceso de entrenamiento.
- Fuente de datos utilizada.
- Justificación de la elección del algoritmo.

### Beneficio
Aporta valor académico y técnico durante la sustentación.

---

## 4. Reportes Exportables
**Estado:** Pendiente

### Implementar
- Exportación a PDF.
- Exportación a Excel.
- Exportación a CSV.

### Reportes sugeridos
- Inventario actual.
- Historial de ventas.
- Historial de predicciones.
- Alertas generadas.
- Productos críticos.

### Beneficio
Facilita la toma de decisiones y el uso empresarial.

---

## 5. Dashboard Analítico Avanzado
**Estado:** Parcial

### Agregar indicadores
- Ventas del mes.
- Ventas por categoría.
- Productos más vendidos.
- Productos con mayor crecimiento.
- Productos con stock crítico.
- Total de alertas activas.
- Predicciones recientes.

### Beneficio
Mejora la visualización de indicadores estratégicos.

---

## 6. Validaciones de Formularios
**Estado:** No evidenciado

### Implementar
- Validación de campos obligatorios.
- Prevención de registros duplicados.
- Validación de cantidades negativas.
- Validación de precios inválidos.
- Validación de fechas incorrectas.

### Beneficio
Incrementa la calidad de los datos almacenados.

---

## 7. Alertas Inteligentes Avanzadas
**Estado:** Parcial

### Agregar
- Alerta de riesgo de desabastecimiento.
- Alerta de sobreinventario.
- Alerta de alta demanda proyectada.
- Recomendaciones automáticas de compra.

### Beneficio
Mejora la capacidad predictiva del sistema.

---

## 8. Preparación para la Sustentación Final
**Estado:** Recomendado

### Preparar
- Arquitectura del sistema.
- Modelo entidad-relación.
- Casos de uso.
- Flujo completo del negocio.
- Explicación del modelo predictivo.
- Resultados obtenidos.
- Beneficios para la empresa.

### Beneficio
Facilita la defensa académica del proyecto.

---

## 9. Control de Predicciones por Producto
**Estado:** Completado ✅ (combinado con Selector de Predicción por Categoría)

### Implementado
- Modo de predicción: Por Producto / Por Categoría.
- Selector de categoría con multi-select de productos.
- Opción "Seleccionar todos" para predecir toda la categoría.
- Endpoint `POST /predicciones/predecir-lote` para múltiples productos.
- Barra de progreso durante predicción en lote.
- Resumen de éxitos/fallidos al finalizar.

### Beneficio
Mantiene la base de datos limpia y permite predicciones masivas eficientes.

---

## 10. Selector de Modelos IA
**Estado:** Completado ✅

### Implementado
- Selector de modelo en frontend (XGBoost / LightGBM).
- Endpoint acepta `id_modelo` opcional.
- Tabla comparativa de modelos con métricas.
- Modelo activo se selecciona por defecto.
- Módulo de Modelos IA con gráficos comparativos.
- Activar/Desactivar modelos individualmente.

### Beneficio
Permite comparar predicciones entre diferentes algoritmos.

---

## 11. Control de Acceso por Roles
**Estado:** Completado ✅

### Implementado
- Rol Vendedor (id=3): Solo ve Productos, Categorías, Proveedores, Inventario, Ventas.
- Rol Administrador (id=1) y Sistemas (id=2): Ven todos los módulos.
- Rutas protegidas con componente RoleRoute.
- Redirección automática según rol al iniciar sesión.

### Beneficio
Seguridad y separación de funciones por rol.

---

---

## 12. Mejoras al Motor de Predicción (ml_service.py)
**Estado:** Completado ✅ (29/06/2026)

### Cambios implementados en `backend/app/services/ml_service.py`

#### 12.1 Precio variable en predicción
- **Antes:** Precio constante durante todo el horizonte de predicción.
- **Ahora:** Precio proyectado con variación histórica (promedio ± 10% desviación de últimos 7 días).
- **Impacto:** Modelo considera fluctuaciones de precio en la demanda.

#### 12.2 Festivos dinámicos de Ecuador
- **Antes:** Lista hardcodeada de festivos US (2011-2016): Año Nuevo, 4 de julio, Acción de Gracias, Navidad.
- **Ahora:** Festivos de Ecuador generados dinámicamente por año con algoritmo de Pascua:
  - Fijos: Año Nuevo, Día del Trabajo, Batalla de Pichincha, Independencia de Guayaquil, Primer Grito de Independencia, Día de los Difuntos, Independencia de Cuenca, Navidad.
  - Móviles: Carnaval (lunes y martes), Viernes Santo.
- **Impacto:** `is_holiday` ahora es correcto para cualquier año.

#### 12.3 Suavizado exponencial
- **Antes:** Predicción cruda del modelo se usaba directamente.
- **Ahora:** Mezcla 80% predicción + 20% promedio ponderado exponencial de últimos 7 valores.
- **Impacto** Reduce acumulación de errores en predicciones lejanas (día 30+).

#### 12.4 Corrección de fuga temporal (min_periods)
- **Antes:** `rolling(window=N).mean()` sin `min_periods` → NaN en primeras filas.
- **Ahora:** `rolling(window=N, min_periods=1).mean()` → datos parciales desde la primera fila.
- **Impacto:** Elimina fuga temporal potencial, reduce pérdida de datos.

### Archivos modificados
- `backend/app/services/ml_service.py` (único archivo)

---

## 13. Re-entrenamiento del Modelo con Mejoras
**Estado:** Pendiente 🔲

### Problema
Los scripts de entrenamiento están en `C:\Users\RRHH3\Desktop\VISUAL\ENTRENAMIENTO\src\` (fuera de TESIS). Tienen la lógica de features **original** (sin las mejoras de la sección 12).

### Pasos para continuar (30/06/2026)

#### Paso 1: Leer scripts de entrenamiento
- Leer `03_features.py` → feature engineering original
- Leer `10_mejorar_modelo.py` → entrenamiento v2
- Identificar qué cambios aplicar

#### Paso 2: Aplicar mejoras en scripts de entrenamiento
- Festivos de Ecuador en `03_features.py` y `10_mejorar_modelo.py`
- `min_periods=1` en rolling windows
- Precio variable (si aplica en entrenamiento)

#### Paso 3: Re-entrenar
```bash
cd C:\Users\RRHH3\Desktop\VISUAL\ENTRENAMIENTO\src
python 10_mejorar_modelo.py
```

#### Paso 4: Registrar en BD
```bash
python 09_registrar_modelos_bd.py
```

#### Paso 5: Activar nuevo modelo
- Desde el frontend (módulo Modelos IA)
- O vía API: `PUT /api/modelos-ia/{id}/activar`

### Dependencias necesarias
- Python 3.10+
- xgboost, lightgbm, scikit-learn, pandas, numpy, pymysql, kagglehub, matplotlib, seaborn, pyyaml
- Dataset M5 en Kaggle (descargado por script 01)
- MariaDB corriendo en puerto 3307

### Notas
- El script 10 también necesita `prophet` (no está en requirements.txt)
- Los modelos generados se guardan en `ENTRENAMIENTO\models\`
- Después de copiar a `TESIS\backend\ml_models\`, reiniciar el backend

---

# Resumen General

## Completado ✅
- Dashboard funcional.
- Gestión de productos.
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
- **Mejoras al motor de predicción (precio variable, festivos Ecuador, suavizado, min_periods).**

## Pendiente 🔲
1. Exportación de reportes.
2. Dashboard analítico avanzado.
3. Validaciones robustas.
4. Alertas inteligentes avanzadas.
5. Preparación de documentación para sustentación.
6. **Re-entrenar modelo con mejoras aplicadas.**
