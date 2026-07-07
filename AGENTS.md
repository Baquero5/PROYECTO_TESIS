# SmartInventory AI - Project Memory

## Project Overview
Thesis project for a university program. SmartInventory AI: inventory management system with ML demand prediction.

## Tech Stack
- Frontend: React (Vite) - http://localhost:5173
- Backend: FastAPI (Python) - http://localhost:8000
- Database: MariaDB - port 3307, user root, password 123456, database tesis_inventario
- ML: XGBoost + LightGBM ensemble (models in backend/ml_models/)
- Active model: LightGBM v2.0 (lightgbm_v2_model.pkl)

## Environment Setup
- Backend venv: D:\visual\TESIS\backend\venv
- Start scripts: iniciar.bat (paths fixed from C:\Users\RRHH3\Desktop\VISUAL\TESIS to D:\visual\TESIS)
- DB config in backend/app/core/config.py: mysql+aiomysql://root:123456@localhost:3307/tesis_inventario

## Tutor Requirements (Msc. Delia)
- KPIs/insights are the most critical part
- Checklist in D:\checklist_correcciones_prediccion.md
- Tareas pendientes en D:\tareas_inventai.md

## Completed Tasks

### 1. Environment and Setup
- Re-cloned repository from GitHub (clean slate)
- Installed backend venv + all pip dependencies
- Installed frontend npm dependencies
- Ran ML training pipeline scripts 01-09 successfully
- Applied DB migration (migrar_bd.py) adding columns: archivo_modelo, parametros, estado, confianza_min, confianza_max, horizonte_dias, porcentaje_confianza
- Manually added missing r2 column to modelos_ia table
- Registered 4 models in DB (XGBoost v1/v2, LightGBM v1/v2; LightGBM v2.0 is ACTIVO)
- Copied model .pkl files to backend/ml_models/
- Fixed iniciar.bat paths
- Fixed config.py DATABASE_URL (added password, port 3307)

### 2. Task 1 - KPIs de Rentabilidad
- New endpoint: /api/predicciones/kpis in prediccion_routes.py
- Schema: KPIsResponse, KPIPrediccion in schemas/prediccion.py
- Frontend: KPI cards + table in Prediccion.jsx
- CSS variables added to index.css (--success-light, --warning-light, --info-light, --danger-light)

### 3. Task 2 - Selector de Fecha de Inicio
- Added fecha_inicio field to PrediccionRequest, PrediccionBatchRequest schemas
- Added to both /predecir and /predecir-lote endpoints
- Frontend: date input field in Prediccion.jsx

### 4. Bug Fix - Route Ordering
- /kpis route was being captured by /{prediccion_id} parameter
- Fixed by moving /kpis BEFORE /{prediccion_id} in route definitions
- Removed duplicate /kpis endpoint at end of file

### 5. Task 3 - Variables de Rentabilidad
- Added precio_venta, precio_compra, ingreso_esperado, ganancia_esperada, margen_porcentaje to PrediccionResponse
- GET /predicciones now JOINs with productos table for prices
- Frontend table updated with new columns

### 6. Task 4 - Rango de Fechas Flexible
- Replaced fixed horizonte dropdown with Fecha Inicio + Fecha Fin date pickers
- Auto-calculates horizonte in days via calcularHorizonte()

### 7. Dashboard Simplification
- Removed Valor Inventario and Predicciones KPIs per user request
- Kept 5 KPIs: Total Productos, Ventas Totales, Stock Critico, Alertas Activas, Reabastecimientos

### 8. Date Bug Fix (2036 dates)
- Problem: Predictions showed year 2036 instead of 2026
- Root cause: prediccion_routes.py had wrong date adjustment logic that doubled the offset
- Old code: delta = fecha_inicio - fecha_original; fecha_pred = fecha_inicio + delta (doubles offset)
- Fix: Calculate offset ONCE using first prediction, apply uniformly to all predictions
- Fixed in both /predecir and /predecir-lote endpoints
- Deleted 18 wrong predictions with year 2036 from DB

### 9. Duplicate Prediction Prevention
- Problem: Re-predicting the same product created duplicate records in DB
- Solution: Delete existing predictions for product before creating new ones
- Added delete_by_product() to PrediccionRepository
- Implemented in both /predecir and /predecir-lote endpoints
- Implemented in branch: feature/predecir-sin-duplicados

### 10. Sistema de Subcategorías (04/07/2026)
- Created table `subcategorias` with 24 subcategories (10 Alimentos, 7 Hogar, 7 Deportes)
- New files: subcategorias.py (model), subcategoria.py (schema), subcategoria_repository.py, subcategoria_routes.py (endpoints)
- CRUD complete: GET /api/subcategorias, GET /api/subcategorias/categoria/{id}, POST, PUT, DELETE
- FK `id_subcategoria` added to `productos` table (nullable for existing products)
- Frontend: Subcategorias.jsx page with CRUD, search, filter by category
- Route: /subcategorias in App.jsx, nav link in Layout.jsx

### 11. Asignación de Subcategorías a Productos (04/07/2026)
- All 1000 products assigned to subcategories using keyword-based script
- Distribution: Alimentos (686 products), Hogar (235), Deportes (79)
- Field `id_subcategoria` is now REQUIRED for new products (schema + frontend validation)
- Products.jsx: Dynamic subcategory select that filters by selected category

### 12. Selector Subcategoría en Predicción (04/07/2026)
- Added subcategory filter in Prediccion.jsx
- Products filter by BOTH category and subcategory
- Subcategory resets when category changes
- Loaded via api.get('/subcategorias')

### 13. Filtro Modelos Activos en Predicción (04/07/2026)
- Model selector now only shows models with `estado === 'ACTIVO'`
- Applied in Prediccion.jsx model select dropdown

### 14. Columna Venta Promedio por Día (04/07/2026)
- Backend: /kpis endpoint now calculates `venta_promedio_diaria` using last 90 days sales
- Added LEFT JOIN to subquery that sums sales from detalle_ventas
- Schema: `venta_promedio_diaria` field added to KPIPrediccion
- Frontend: New "Prom. Diario" column in KPIs table

### 15. Encabezado Resumen de Predicciones (04/07/2026)
- Added summary card above "Historial de Predicciones" table
- Shows: Date range, products included, total predictions, total estimated demand
- Uses getResumenPredicciones() function

### 16. Modelo Acotado a Alimentos (05/07/2026)
- Filtered training dataset to only Alimentos category (697K rows from 17.6M)
- Created 5 subcategory-specific models: Lácteos, Frutas, Bebidas, Carnes, Snacks (20 products each = 100 total)
- Model files: ensemble_v2_alimentos.pkl, lightgbm_v2_alimentos.pkl, xgboost_v2_alimentos.pkl
- Ensemble R²=0.675 (XGBoost 0.45 + LightGBM 0.55)
- Backend: ml_service.py prioritizes alimentos models, _load_model_scope() detects alcance
- Endpoint: GET /api/predicciones/modelos/alcance returns subcategorias and total_productos
- Frontend: Blue info banner shows model scope, category dropdown disabled when scoped
- Subcategory dropdown filtered by model scope

### 17. Dropdown Personalizado de Productos (05/07/2026)
- Replaced native <select> with custom checkbox dropdown
- Shows "Seleccionar productos..." / "N seleccionado(s)" / "Todos (N)"
- Opens panel with checkboxes, sticky "Todos" checkbox
- Click outside closes dropdown
- Uses productosSeleccionados state (array of IDs)

### 18. Dropdown Personalizado de Modelos (05/07/2026)
- Same custom dropdown pattern for Modelo IA selection
- Supports selecting 1 or 2 models (max 2)
- 1 model → generates predictions normally
- 2 models → generates predictions for BOTH + shows comparison automatically
- Radio-style selection with highlight

### 19. Comparación de Modelos (05/07/2026)
- Backend: POST /api/predicciones/predecir-comparar endpoint
- Schema: PrediccionCompararRequest (id_productos, id_modelos, horizonte_dias, fecha_inicio)
- Response: PrediccionCompararResponse with per-product, per-model predictions
- Frontend: When 2 models selected, "Generar Predicción" generates both AND shows comparison
- Comparison chart: Line chart with 1 color per model overlaid
- Comparison table: Predictions side by side + difference % + average row
- ErrorBoundary component catches render crashes gracefully
- Fixed: loadData() no longer resets modelosSeleccionados
- Fixed: react-chartjs-2 data prop must be object, not function

### 20. Optimización de Predecir-Lote (05/07/2026)
- BEFORE: Sequential loop - 100 queries + 100 ML predictions + 100 deletes + 100 inserts
- AFTER: Batch query (1 SQL with IN) + Parallel ML (asyncio.Semaphore(4)) + Batch writes
- Repository: Added delete_by_products() and create_many_no_commit()
- Performance: 5 products in ~4s (was ~15s sequential)
- Uses asyncio.to_thread() for CPU-bound predict_demand
- Single transaction for all DB writes

### 21. Testing Completo (05/07/2026)
- Created test_endpoints.py - automated testing of all endpoints
- All 15 endpoints tested and working:
  - Login ✅, Products ✅, Categories ✅, Subcategories ✅, Models ✅
  - Model Scope ✅, KPIs ✅, Predictions ✅, Batch Predict ✅
  - Model Comparison ✅, Sales ✅, Alerts ✅, Inventory ✅, Suppliers ✅
- Bugs fixed: model=None in ensemble, missing 'leida' column in alertas table

### 22. Gráficos Mejorados - Tooltips, Exportación, Sparklines (06/07/2026)
- New components: SparkLine.jsx (mini charts for KPIs), ChartExportButton.jsx (export chart as PNG/JPEG)
- New utility: config/chartConfig.js with formatters (formatCurrency, formatNumber, formatDateFull), chart colors, tooltip configs, and reusable chart options
- Dashboard.jsx: Added sparklines to all 4 KPI cards, export buttons on all 6 charts, enhanced tooltips with formatted values, better animations (900ms easeOutQuart), hover effects on cards
- Prediccion.jsx: Added export button to prediction chart, enhanced tooltips with confidence range display, consistent currency formatting, KPI cards with gradient backgrounds
- exportService.js: Added exportChartAsImage() utility function
- index.css: Added styles for chart-export-btn, chart-card hover effects, loading spinner, KPI animations, empty states
- All charts now use centralized config for consistent styling and formatting

## Remaining Tasks
- Exportar historial a Excel: Funciona con ExportButtons (CSV/Excel/PDF), limitado a 200 registros
- Predicción por categoría: Funciona con filtro + "Todos", no hay endpoint dedicado

---

## Frontend Analysis - Pendientes por Implementar (06/07/2026)

### 🔴 CRÍTICOS (hacer primero - previenen bugs y mejoran UX base)

| # | Problema | Páginas | Solución |
|---|----------|---------|----------|
| 1 | `window.confirm()` para eliminar | Todas (10 páginas CRUD) | Crear componente `<ConfirmDialog>` |
| 2 | Sin estado `submitting` en formularios | Todas (14 páginas) | Agregar loading al botón para prevenir doble-click |
| 3 | Modal sin click-to-close en backdrop | Todas con modal (10) | Agregar `onClick` al backdrop div |

### 🟠 ALTOS (mayor impacto visual y UX)

| # | Problema | Páginas | Solución |
|---|----------|---------|----------|
| 4 | Inline styles en botones (btn-danger, btn-success) | Todas | Crear clases CSS `.btn-danger`, `.btn-success` |
| 5 | Sin paginación en tablas | Todas (14) | Crear componente `<Pagination>` |
| 6 | Search inputs con estilos inline repetidos | 10 páginas | Crear clase `.search-input` |
| 7 | Loading es solo texto "Cargando..." | 12 páginas | Usar spinner existente `.loading-spinner` |
| 8 | Empty states inconsistentes | Todas | Crear componente `<EmptyState>` |
| 9 | Estilos inline masivos en modales | Todas | Crear `.modal-overlay`, `.modal-content` |

### 🟡 MEDIOS (nice-to-have)

| # | Problema | Páginas | Solución |
|---|----------|---------|----------|
| 10 | Sin navegación por teclado en modals (Escape) | Todas | Agregar useEffect para Escape key |
| 11 | Sin aria-labels para accesibilidad | Todas | Agregar labels |
| 12 | Formato de fecha inconsistente | Múltiples | Crear utilidad `formatDate()` |
| 13 | Sin responsive en tablas | Todas | Agregar scroll horizontal o card view |

### 📦 Componentes Reutilizables a Crear

| Componente | Reemplaza | Uso |
|------------|-----------|-----|
| `<ConfirmDialog>` | `window.confirm()` | Eliminar registros |
| `<Modal onClose={...}>` | Divs inline | Todos los modales con backdrop + Escape |
| `<Skeleton type="table\|card\|text">` | "Cargando..." | Loading states |
| `<Pagination page={} totalPages={} onChange={}>` | Sin paginación | Todas las tablas |
| `<SearchInput value={} onChange={} placeholder="">` | Inputs inline | Búsquedas |
| `<EmptyState icon="" message="">` | Texto plano | Estados vacíos |
| `<SubmitButton loading={} disabled={}>` | Botones simples | Prevenir doble-click |

### 📋 Pendientes por Módulo

| Módulo | Pendientes Críticos/Altos |
|--------|---------------------------|
| Alertas.jsx | ConfirmDialog, submit loading, backdrop close, fix tildes ("Accion"→"Acción", "Criticas"→"Críticas") |
| Categorias.jsx | ConfirmDialog, submit loading, backdrop close |
| Dashboard.jsx | Skeleton loading, lazy load charts |
| InventarioPage.jsx | ConfirmDialog, submit loading, backdrop close |
| Login.jsx | Password visibility toggle, "olvidé mi contraseña" |
| ModelosIA.jsx | Confirmación activar/desactivar, quitar botones duplicados |
| Prediccion.jsx | Búsqueda en dropdown productos, validación fechas, memoizar chartOptions |
| Productos.jsx | ConfirmDialog, submit loading, formato moneda precios, responsive tabla |
| Proveedores.jsx | ConfirmDialog, submit loading, helper text RUC |
| Reportes.jsx | Indicador progreso exportación, lazy load datos, filtro fecha |
| Roles.jsx | ConfirmDialog, submit loading, advertencia cambios sin guardar |
| Subcategorias.jsx | ConfirmDialog, submit loading, conteo productos |
| Usuarios.jsx | ConfirmDialog, submit loading, toggle password, contraseña opcional en edición |
| Ventas.jsx | Implementar "Ver Detalle", submit loading, precio solo lectura, fecha en tabla, búsqueda en dropdown |

---

## Key Files
- frontend/src/pages/Prediccion.jsx: Main prediction page (KPIs, date range, subcategory filter, custom dropdowns, model comparison, comparison chart+table)
- frontend/src/pages/Dashboard.jsx: Dashboard with 5 KPIs
- frontend/src/pages/Subcategorias.jsx: Subcategories CRUD page
- frontend/src/pages/Productos.jsx: Products with subcategory select
- frontend/src/index.css: CSS variables
- frontend/src/components/Layout.jsx: Navigation with subcategories link
- frontend/src/components/ExportButtons.jsx: Reusable export dropdown (CSV, Excel, PDF)
- frontend/src/services/exportService.js: Client-side export logic (xlsx, jspdf)
- frontend/src/components/SparkLine.jsx: Mini sparkline chart for KPI cards
- frontend/src/components/ChartExportButton.jsx: Export chart as PNG/JPEG button
- frontend/src/config/chartConfig.js: Chart.js utilities (formatters, colors, tooltip configs, chart options)
- frontend/src/services/exportService.js: Export utilities including exportChartAsImage()
- backend/app/presentation/prediccion_routes.py: ALL prediction endpoints: /, /kpis, /modelos/alcance, /predecir-comparar, /predecir, /predecir-lote
- backend/app/presentation/subcategoria_routes.py: Subcategory CRUD endpoints
- backend/app/presentation/alerta_routes.py: Alert endpoints
- backend/app/schemas/prediccion.py: All schemas including KPIsResponse, PrediccionCompararRequest/Response
- backend/app/repositories/prediccion_repository.py: Prediction CRUD + batch methods (delete_by_products, create_many_no_commit)
- backend/app/services/ml_service.py: ML prediction logic with ensemble support and model scope detection
- backend/app/core/config.py: DATABASE_URL with correct password/port
- backend/ml_models/ensemble_v2_alimentos.pkl: Active ensemble model (XGBoost+LightGBM, R²=0.675)
- ml_training/src/14_dataset_filtrado.py: Dataset filter for Alimentos
- ml_training/src/15_entrenar_lightgbm_filtrado.py: LightGBM training
- ml_training/src/16_entrenar_xgboost_filtrado.py: XGBoost training
- ml_training/src/17_ensemble_filtrado.py: Ensemble creation
- test_endpoints.py: Automated endpoint testing script
- frontend/src/components/SparkLine.jsx: Mini sparkline chart for KPI cards
- frontend/src/components/ChartExportButton.jsx: Export chart as PNG/JPEG button
- frontend/src/config/chartConfig.js: Chart.js utilities (formatters, colors, tooltip configs, chart options)
- frontend/src/services/exportService.js: Export utilities including exportChartAsImage()

## Key Behaviors to Know
- predict_demand in ml_service.py is deterministic: same input produces same output
- predecir endpoint deletes old predictions before creating new ones (no duplicates)
- KPIs endpoint requires existing predictions in DB to show data
- calcularHorizonte() in Prediccion.jsx computes days between fechaInicio and fechaFin
- Subcategory filter in Prediccion.jsx filters products by both category AND subcategory
- Model selector shows ACTIVO models only, supports 1 or 2 selections
- 2 models selected → "Generar Predicción" generates both AND shows comparison
- Comparison chart data prop must be object (not function) for react-chartjs-2
- predecir-lote uses batch query + asyncio.Semaphore(4) for parallel ML
- login requires correo (not username) + password
- Admin user: admin@sistema.com / admin123
- ErrorBoundary wraps comparison section to prevent blank screen on render errors
- loadData() no longer resets modelosSeleccionados on re-fetch
