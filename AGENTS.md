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

## Remaining Tasks
- Task #5: Exportar historial a Excel (ExportButtons component already exists, limit of 50 records needs removal)
- Task #6: Verificar prediccion por categoria (code reviewed, correct, needs manual test with 235 products)
- Optimize predecir-lote performance (235 products takes 5+ min due to sequential processing)

## Key Files
- frontend/src/pages/Prediccion.jsx: Main prediction page (tasks 1-4, date fix)
- frontend/src/pages/Dashboard.jsx: Dashboard with 5 KPIs
- frontend/src/index.css: CSS variables
- backend/app/presentation/prediccion_routes.py: All prediction endpoints including /kpis
- backend/app/schemas/prediccion.py: Updated schemas with KPIs, rentability fields, fecha_inicio
- backend/app/repositories/prediccion_repository.py: Prediction CRUD operations
- backend/app/services/ml_service.py: ML prediction logic (predict_demand, prepare_features)
- backend/app/core/config.py: DATABASE_URL with correct password/port
- ml_training/src/migrar_bd.py: DB migration script
- iniciar.bat: Startup script (fixed paths)
- Pendientes_SmartInventory_AI.md: Original task checklist
- D:\checklist_correcciones_prediccion.md: Tutor revision checklist

## Key Behaviors to Know
- predict_demand in ml_service.py is deterministic: same input produces same output
- predecir endpoint deletes old predictions before creating new ones (no duplicates)
- KPIs endpoint requires existing predictions in DB to show data
- calcularHorizonte() in Prediccion.jsx computes days between fechaInicio and fechaFin
