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

## Pendiente 🔲
1. Exportación de reportes.
2. Dashboard analítico avanzado.
3. Validaciones robustas.
4. Alertas inteligentes avanzadas.
5. Preparación de documentación para sustentación.
