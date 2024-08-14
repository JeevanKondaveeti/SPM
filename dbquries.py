import mysql.connector
def connect():
    mydb = mysql.connector.connect(user='root',password='admin',db='spm',host='localhost')
    if mydb.is_connected():
        return "Connected"
    else:
        return "Database not connected"