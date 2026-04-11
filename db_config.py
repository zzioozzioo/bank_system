import oracledb

db_config = {
    "user": "C##BANK_SYSTEM",
    "password": "1234",
    "dsn": "localhost:1521/FREE"
}

def get_connection():
    try:
        return oracledb.connect(**db_config)
    except Exception as e:
        print(f"DB 연결 실패: {e}")
        return None