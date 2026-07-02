# Memoria de Trabajo - SmartInventory AI

## Registro de Desarrollo

### Sesion: Correcciones del Tutor y Bug Fechas

#### Contexto
El tutor (Msc. Delia) proporciono una lista de correcciones en `D:\checklist_correcciones_prediccion.md`. Se procedio a implementar cada punto.

#### Tareas Completadas

**1. KPIs de Rentabilidad**
- Se creo endpoint `GET /api/predicciones/kpis` que calcula: total productos, ingreso total esperado, ganancia total esperada, costo total esperado, producto de mayor volumen, mayor rentabilidad, mayor ingreso
- Se agregaron schemas `KPIsResponse` y `KPIPrediccion`
- Frontend: tarjetas KPI + tabla detallada en Prediccion.jsx
- Variables CSS: --success-light, --warning-light, --info-light, --danger-light

**2. Selector de Fecha de Inicio**
- Campo `fecha_inicio` agregado a schemas PrediccionRequest y PrediccionBatchRequest
- Disponible en endpoints /predecir y /predecir-lote
- Frontend: input de tipo date

**3. Bug Rutas - Correccion**
- `/kpis` estaba siendo capturada por `/{prediccion_id}` (parametro dinamico)
- Solucion: mover `/kpis` ANTES de `/{prediccion_id}` en las definiciones de rutas
- Se elimino endpoint duplicado de /kpis al final del archivo

**4. Variables de Rentabilidad**
- Campos agregados a PrediccionResponse: precio_venta, precio_compra, ingreso_esperado, ganancia_esperada, margen_porcentaje
- GET /predicciones ahora hace JOIN con tabla productos para obtener precios
- Frontend: columnas actualizadas en tabla de predicciones

**5. Rango de Fechas Flexible**
- Se reemplazo el dropdown fijo de horizonte con selectores Fecha Inicio + Fecha Fin
- Funcion calcularHorizonte() calcula automaticamente los dias entre ambas fechas

**6. Simplificacion del Dashboard**
- Se eliminaron KPIs "Valor Inventario" y "Predicciones" por indicacion del tutor
- Se mantienen 5 KPIs: Total Productos, Ventas Totales, Stock Critico, Alertas Activas, Reabastecimientos

**7. Fix: Bug de Fechas (Ano 2036)**
- Problema: Las predicciones mostraban ano 2036 en lugar de 2026
- Causa raiz: logica de ajuste de fechas en prediccion_routes.py duplicaba el offset
  - Codigo viejo: `delta = fecha_inicio - fecha_original; fecha_pred = fecha_inicio + delta` (duplica offset)
- Solucion: Calcular offset UNA sola vez usando la primera prediccion, aplicar uniformemente a todas
- Corregido en ambos endpoints: /predecir y /predecir-lote
- Se eliminaron 18 predicciones con ano 2036 de la base de datos

**8. Eliminacion de Predicciones Duplicadas**
- Problema: re-predecir un producto creaba registros duplicados en la DB
- Solucion: antes de crear nuevas predicciones, eliminar las existentes del producto
- Implementado en ambos endpoints: /predecir y /predecir-lote
- Metodo delete_by_product() agregado a PrediccionRepository
- Implementado en rama feature/predecir-sin-duplicados

#### Pendientes
- Task #5: Exportar historial a Excel (componente ExportButtons ya existe)
- Task #6: Verificar prediccion por categoria

#### Notas Tecnicas
- El modelo ML es determinista: misma entrada produce misma salida
- Endpoint predecir elimina predicciones anteriores antes de crear nuevas (sin duplicados)
- KPIs requieren predicciones existentes en DB para mostrar datos
