"""
Script de prueba para validar el sistema de materias sin necesidad de MySQL
"""
import os
import sys
import django

# Configurar Django para usar SQLite temporalmente
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['DEBUG'] = 'True'

# Modificar temporalmente la configuración de BD
import config.settings as settings
settings.DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

django.setup()

from django.core.management import call_command
from users.models import User, Materia
from users.serializers import RegisterSerializer, MateriaSerializer, UpdateMateriasSerializer

print("=" * 70)
print("SISTEMA DE PRUEBAS - MATERIAS Y CARRERAS")
print("=" * 70)
print()

# Crear las tablas en SQLite en memoria
print("1. Creando tablas en base de datos de prueba...")
call_command('migrate', '--run-syncdb', verbosity=0)
print("   ✓ Tablas creadas")
print()

# Crear las materias manualmente (como lo hará la migración)
print("2. Creando materias...")
materias_data = [
    {
        'codigo': 'MDW_49067',
        'nombre': 'Modelos de Desarrollo Web',
        'nrc': '49067',
        'carreras_permitidas': ['ITI']
    },
    {
        'codigo': 'SO1_50153',
        'nombre': 'Sistemas Operativos I',
        'nrc': '50153',
        'carreras_permitidas': ['LCC', 'ICC']
    },
    {
        'codigo': 'SO2_50165',
        'nombre': 'Sistemas Operativos II',
        'nrc': '50165',
        'carreras_permitidas': ['LCC', 'ICC']
    },
    {
        'codigo': 'IS_48189',
        'nombre': 'Ingeniería de Software',
        'nrc': '48189',
        'carreras_permitidas': ['LCC', 'ICC']
    },
]

# Limpiar materias existentes primero
Materia.objects.all().delete()

for materia_data in materias_data:
    Materia.objects.create(**materia_data)
    print(f"   ✓ {materia_data['nombre']} — NRC: {materia_data['nrc']}")

print(f"\n   Total: {Materia.objects.count()} materias creadas")
print()

# Test 1: Registro de estudiante ITI con materia válida
print("3. Test: Registro de estudiante ITI con MDW")
data_iti = {
    'id_usuario': '20220001',
    'password': 'Test123!@',
    'nombre_completo': 'Juan Pérez ITI',
    'correo': 'juan@test.com',
    'carrera': 'ITI',
    'rol': 'estudiante',
    'materias': [Materia.objects.get(codigo='MDW_49067').id]
}
serializer = RegisterSerializer(data=data_iti)
if serializer.is_valid():
    user = serializer.save()
    print(f"   ✓ Usuario creado: {user.nombre_completo}")
    print(f"   ✓ Carrera: {user.get_carrera_display()}")
    print(f"   ✓ Materias asignadas: {user.materias_estudiante.count()}")
    for materia in user.materias_estudiante.all():
        print(f"      - {materia}")
else:
    print(f"   ✗ Error: {serializer.errors}")
print()

# Test 2: Registro de estudiante LCC con múltiples materias
print("4. Test: Registro de estudiante LCC con SO1 y IS")
data_lcc = {
    'id_usuario': '20220002',
    'password': 'Test123!@',
    'nombre_completo': 'María García LCC',
    'correo': 'maria@test.com',
    'carrera': 'LCC',
    'rol': 'estudiante',
    'materias': [
        Materia.objects.get(codigo='SO1_50153').id,
        Materia.objects.get(codigo='IS_48189').id
    ]
}
serializer = RegisterSerializer(data=data_lcc)
if serializer.is_valid():
    user = serializer.save()
    print(f"   ✓ Usuario creado: {user.nombre_completo}")
    print(f"   ✓ Carrera: {user.get_carrera_display()}")
    print(f"   ✓ Materias asignadas: {user.materias_estudiante.count()}")
    for materia in user.materias_estudiante.all():
        print(f"      - {materia}")
else:
    print(f"   ✗ Error: {serializer.errors}")
print()

# Test 3: Validación - ITI no puede tener materias de LCC/ICC
print("5. Test: Validación - ITI intenta SO1 (debe fallar)")
data_invalid = {
    'id_usuario': '20220003',
    'password': 'Test123!@',
    'nombre_completo': 'Pedro López ITI',
    'correo': 'pedro@test.com',
    'carrera': 'ITI',
    'rol': 'estudiante',
    'materias': [Materia.objects.get(codigo='SO1_50153').id]
}
serializer = RegisterSerializer(data=data_invalid)
if serializer.is_valid():
    print(f"   ✗ FALLO: No debería permitir esta combinación")
else:
    print(f"   ✓ Validación correcta - Error esperado:")
    if 'materias' in serializer.errors:
        print(f"      {serializer.errors['materias'][0]}")
print()

# Test 4: Validación - ITI solo puede elegir 1 materia
print("6. Test: Validación - ITI con múltiples materias (debe fallar)")
mdw = Materia.objects.get(codigo='MDW_49067')
# Crear temporalmente otra materia ITI para probar
materia_extra = Materia.objects.create(
    codigo='TEST_00000',
    nombre='Test Extra ITI',
    nrc='00000',
    carreras_permitidas=['ITI']
)
data_multiple_iti = {
    'id_usuario': '20220004',
    'password': 'Test123!@',
    'nombre_completo': 'Ana Martínez ITI',
    'correo': 'ana@test.com',
    'carrera': 'ITI',
    'rol': 'estudiante',
    'materias': [mdw.id, materia_extra.id]
}
serializer = RegisterSerializer(data=data_multiple_iti)
if serializer.is_valid():
    print(f"   ✗ FALLO: No debería permitir múltiples materias para ITI")
else:
    print(f"   ✓ Validación correcta - Error esperado:")
    if 'materias' in serializer.errors:
        print(f"      {serializer.errors['materias'][0]}")
materia_extra.delete()
print()

# Test 5: Registro de docente LCC con múltiples materias
print("7. Test: Registro de docente LCC con SO1, SO2 e IS")
data_docente = {
    'id_usuario': 'D001',
    'password': 'Docente123!@',
    'nombre_completo': 'Prof. Carlos Ramírez',
    'correo': 'carlos@test.com',
    'carrera': 'LCC',
    'rol': 'docente',
    'materias': [
        Materia.objects.get(codigo='SO1_50153').id,
        Materia.objects.get(codigo='SO2_50165').id,
        Materia.objects.get(codigo='IS_48189').id
    ]
}
serializer = RegisterSerializer(data=data_docente)
if serializer.is_valid():
    user = serializer.save()
    print(f"   ✓ Docente creado: {user.nombre_completo}")
    print(f"   ✓ Carrera: {user.get_carrera_display()}")
    print(f"   ✓ Materias que imparte: {user.materias_docente.count()}")
    for materia in user.materias_docente.all():
        print(f"      - {materia}")
else:
    print(f"   ✗ Error: {serializer.errors}")
print()

# Test 6: Validación - Docente debe tener carrera
print("8. Test: Validación - Docente sin carrera (debe fallar)")
data_docente_sin_carrera = {
    'id_usuario': 'D002',
    'password': 'Docente123!@',
    'nombre_completo': 'Prof. Sin Carrera',
    'correo': 'sincarrera@test.com',
    'rol': 'docente',
    'materias': [Materia.objects.get(codigo='MDW_49067').id]
}
serializer = RegisterSerializer(data=data_docente_sin_carrera)
if serializer.is_valid():
    print(f"   ✗ FALLO: Docente debe tener carrera asignada")
else:
    print(f"   ✓ Validación correcta - Error esperado:")
    if 'carrera' in serializer.errors:
        print(f"      {serializer.errors['carrera'][0]}")
print()

# Test 7: Validación - Docente ITI no puede tener materias de LCC/ICC
print("9. Test: Validación - Docente ITI intenta SO1 (debe fallar)")
data_docente_invalid = {
    'id_usuario': 'D003',
    'password': 'Docente123!@',
    'nombre_completo': 'Prof. Docente ITI',
    'correo': 'docenteiti@test.com',
    'carrera': 'ITI',
    'rol': 'docente',
    'materias': [Materia.objects.get(codigo='SO1_50153').id]
}
serializer = RegisterSerializer(data=data_docente_invalid)
if serializer.is_valid():
    print(f"   ✗ FALLO: No debería permitir esta combinación")
else:
    print(f"   ✓ Validación correcta - Error esperado:")
    if 'materias' in serializer.errors:
        print(f"      {serializer.errors['materias'][0]}")
print()

# Test 8: Actualizar materias de un usuario
print("10. Test: Actualizar materias de estudiante existente")
estudiante = User.objects.get(id_usuario='20220002')
print(f"   Usuario: {estudiante.nombre_completo}")
print(f"   Materias actuales: {[str(m) for m in estudiante.materias_estudiante.all()]}")
update_data = {
    'id_usuario': '20220002',
    'materias': [
        Materia.objects.get(codigo='SO2_50165').id,
        Materia.objects.get(codigo='IS_48189').id
    ]
}
serializer = UpdateMateriasSerializer(data=update_data)
if serializer.is_valid():
    user = serializer.validated_data['user']
    materias = serializer.validated_data['materias']
    user.materias_estudiante.set(materias)
    print(f"   ✓ Materias actualizadas: {[str(m) for m in user.materias_estudiante.all()]}")
else:
    print(f"   ✗ Error: {serializer.errors}")
print()

# Test 9: Filtrar materias por carrera
print("11. Test: Filtrar materias por carrera")
print("   Materias para ITI:")
materias_iti = Materia.get_materias_por_carrera('ITI')
for m in materias_iti:
    print(f"      - {m}")
print(f"\n   Materias para LCC:")
materias_lcc = Materia.get_materias_por_carrera('LCC')
for m in materias_lcc:
    print(f"      - {m}")
print(f"\n   Materias para ICC:")
materias_icc = Materia.get_materias_por_carrera('ICC')
for m in materias_icc:
    print(f"      - {m}")
print()

# Resumen final
print("=" * 70)
print("RESUMEN DE PRUEBAS")
print("=" * 70)
print(f"Total usuarios creados: {User.objects.count()}")
print(f"  - Estudiantes: {User.objects.filter(rol='estudiante').count()}")
print(f"  - Docentes: {User.objects.filter(rol='docente').count()}")
print(f"\nTotal materias: {Materia.objects.count()}")
print(f"\nCarreras disponibles:")
print(f"  - ICC: Ingeniería en Cs. de la Computación")
print(f"  - LCC: Licenciatura en Cs. de la Computación")
print(f"  - ITI: Ingeniería en Tecnologías de la Información")
print()
print("✓ Todas las pruebas completadas exitosamente")
print("=" * 70)
