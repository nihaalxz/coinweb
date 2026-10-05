# PyMySQL as MySQLdb for seamless cross-platform MySQL support in Django
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
