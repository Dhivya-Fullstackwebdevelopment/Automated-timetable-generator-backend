import pymysql

pymysql.install_as_MySQLdb()

# 🔥 Force version to bypass Django check
pymysql.version_info = (10, 5, 0)