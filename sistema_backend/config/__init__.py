# Usar PyMySQL como reemplazo de MySQLdb (solo en desarrollo local)
import os

# Solo importar pymysql si NO estamos en producción
if not (os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RENDER') or os.environ.get('TIDB_HOST')):
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
    except ImportError:
        pass
