#!/usr/bin/env python
"""
Script para migrar usuarios desde database/users.json a MySQL
Ejecutar después de las migraciones de Django
"""
import os
import sys
import json
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from users.models import User

# Ruta al archivo JSON de usuarios
USERS_JSON_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'database',
    'users.json'
)


def migrate_users():
    """Migrar usuarios desde JSON a MySQL"""
    
    print("=" * 60)
    print("MIGRACIÓN DE USUARIOS - JSON a MySQL")
    print("=" * 60)
    
    # Verificar que existe el archivo
    if not os.path.exists(USERS_JSON_PATH):
        print(f"❌ Error: No se encontró el archivo {USERS_JSON_PATH}")
        return False
    
    # Leer usuarios desde JSON
    with open(USERS_JSON_PATH, 'r', encoding='utf-8') as f:
        users_data = json.load(f)
    
    print(f"\n📄 Encontrados {len(users_data)} usuarios en users.json")
    
    migrated = 0
    skipped = 0
    errors = 0
    
    for user_data in users_data:
        id_usuario = user_data.get('id_usuario')
        
        try:
            # Verificar si ya existe
            if User.objects.filter(id_usuario=id_usuario).exists():
                print(f"⏭️  Saltando {id_usuario} - ya existe en la base de datos")
                skipped += 1
                continue
            
            # Verificar si el correo ya existe
            correo = user_data.get('correo', '')
            if User.objects.filter(correo__iexact=correo).exists():
                print(f"⏭️  Saltando {id_usuario} - el correo {correo} ya existe")
                skipped += 1
                continue
            
            # Crear usuario preservando el hash de contraseña bcrypt
            user = User(
                id_usuario=id_usuario,
                password=user_data.get('password', ''),  # Ya viene hasheado con bcrypt
                nombre_completo=user_data.get('nombre_completo', ''),
                correo=correo,
                telefono=user_data.get('telefono', ''),
                sexo=user_data.get('sexo', 'Otro'),
                carrera=user_data.get('carrera', ''),
                rol=user_data.get('rol', 'estudiante'),
                is_active=True,
            )
            user.save()
            
            print(f"✅ Migrado: {id_usuario} ({user.nombre_completo}) - {user.rol}")
            migrated += 1
            
        except Exception as e:
            print(f"❌ Error migrando {id_usuario}: {str(e)}")
            errors += 1
    
    print("\n" + "=" * 60)
    print("RESUMEN DE MIGRACIÓN")
    print("=" * 60)
    print(f"✅ Migrados exitosamente: {migrated}")
    print(f"⏭️  Saltados (ya existían): {skipped}")
    print(f"❌ Errores: {errors}")
    print(f"📊 Total procesados: {len(users_data)}")
    
    return errors == 0


def verify_migration():
    """Verificar que los usuarios se migraron correctamente"""
    
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE USUARIOS EN MySQL")
    print("=" * 60)
    
    users = User.objects.all()
    print(f"\n📊 Total de usuarios en la base de datos: {users.count()}\n")
    
    for user in users:
        print(f"  • {user.id_usuario}")
        print(f"    Nombre: {user.nombre_completo}")
        print(f"    Correo: {user.correo}")
        print(f"    Rol: {user.rol}")
        print(f"    Carrera: {user.carrera}")
        print()


if __name__ == '__main__':
    print("\n🚀 Iniciando migración de datos...\n")
    
    success = migrate_users()
    verify_migration()
    
    if success:
        print("\n✅ Migración completada exitosamente!")
    else:
        print("\n⚠️  Migración completada con errores")
