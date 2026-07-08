"""
Script para recrear el usuario admin con hash correcto.
Ejecutar una sola vez: python fix_admin.py
"""
import asyncio
from app.core.database import AsyncSessionLocal, engine, Base
from app.models.usuarios import Usuario
from app.models.roles import Rol
from app.services.auth_service import hash_password
from sqlalchemy import select


async def fix_admin():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Buscar usuario admin
        result = await db.execute(select(Usuario).where(Usuario.correo == "admin@sistema.com"))
        admin = result.scalar_one_or_none()

        if admin:
            # Actualizar contraseña
            admin.password_hash = hash_password("Admin123!")
            admin.estado = True
            await db.commit()
            print("[OK] Contraseña de admin actualizada: admin@sistema.com / Admin123!")
        else:
            # Crear rol admin si no existe
            result = await db.execute(select(Rol).where(Rol.nombre == "ADMINISTRADOR"))
            rol = result.scalar_one_or_none()
            if rol is None:
                rol = Rol(nombre="ADMINISTRADOR", descripcion="Administrador del sistema")
                db.add(rol)
                await db.flush()

            # Crear usuario admin
            admin = Usuario(
                id_rol=rol.id_rol,
                nombres="Administrador",
                apellidos="del Sistema",
                correo="admin@sistema.com",
                password_hash=hash_password("Admin123!"),
                estado=True,
            )
            db.add(admin)
            await db.commit()
            print("[OK] Usuario admin creado: admin@sistema.com / Admin123!")


if __name__ == "__main__":
    asyncio.run(fix_admin())
