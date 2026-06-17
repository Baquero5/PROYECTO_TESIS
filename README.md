# SmartInventory AI

**Sistema de Inteligencia Artificial para la Predicción de Demanda y Optimización de Inventarios en Empresas Comerciales**

Proyecto de tesis - Universidad Estatal Amazónica (UNEMI)

## Autores

- Jordan Cristhian Villa Martinez
- Cristhian Adrian Baquero Vaca

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | FastAPI (Python 3.10) + SQLAlchemy async |
| Frontend | React 19 + Vite + Tailwind CSS |
| Base de datos | MariaDB (puerto 3307) |
| Migraciones | Alembic |
| ML | pandas + scikit-learn |

## Requisitos Previos

- Python 3.10+
- Node.js 18+
- MariaDB (puerto 3307)

## Instalación

### 1. Base de datos

```sql
CREATE DATABASE tesis_inventario;
```

### 2. Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno (editar .env si es necesario)
# DATABASE_URL=mysql+aiomysql://root:123456@localhost:3307/tesis_inventario

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

### 4. Inicio rápido (Windows)

Ejecutar `iniciar.bat` desde la carpeta raíz del proyecto. Inicia backend y frontend automáticamente.

## URLs del Sistema

| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Documentación API | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

## Credenciales por Defecto

| Campo | Valor |
|-------|-------|
| Email | admin@sistema.com |
| Contraseña | Admin123! |

## Estructura del Proyecto

```
TESIS/
├── backend/
│   ├── app/
│   │   ├── core/          # Configuración, BD, dependencias
│   │   ├── models/        # 15 modelos SQLAlchemy
│   │   ├── schemas/       # 14 schemas Pydantic
│   │   ├── repositories/  # 15 repositorios
│   │   ├── services/      # Servicios de negocio
│   │   └── presentation/  # 13 rutas API
│   ├── alembic/           # Migraciones
│   └── seed_data.py       # Datos de prueba
├── frontend/
│   └── src/
│       ├── pages/         # 9 páginas React
│       ├── components/    # Layout, Toast, PrivateRoute
│       ├── context/       # AuthContext
│       └── services/      # API (Axios)
└── iniciar.bat            # Inicio rápido
```

## API Endpoints Principales

- **Auth:** `/api/auth/login`, `/api/auth/register`, `/api/auth/me`
- **Productos:** `/api/products` (CRUD + stats)
- **Categorías:** `/api/categorias` (CRUD)
- **Proveedores:** `/api/proveedores` (CRUD)
- **Inventario:** `/api/inventario` (CRUD + movimientos)
- **Ventas:** `/api/ventas` (CRUD con detalle)
- **Alertas:** `/api/alertas` (CRUD + activas)
- **Predicciones:** `/api/predicciones` (CRUD + por producto)
- **Parámetros:** `/api/parametros-inventario` (CRUD)
- **Reabastecimiento:** `/api/reabastecimiento` (CRUD + pendientes)
- **Datasets:** `/api/datasets` (CRUD)
- **Modelos IA:** `/api/modelos-ia` (CRUD + mejor modelo)
