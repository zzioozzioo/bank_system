import oracledb
import getpass
from db_config import get_connection

def register():
    print("\n--- 회원가입 ---")
    u_id = input("아이디: ").strip().lower() # 소문자로 비교

    if u_id == 'admin':
        print("[!] 'admin'은 관리자 전용 아이디입니다. 다른 아이디를 입력해주세요.")
        return

    u_pw = getpass.getpass("비밀번호: ").strip()
    u_pw_confirm = getpass.getpass("비밀번호 확인: ").strip()
    u_name = input("이름: ").strip()

    if not (u_id and u_pw and u_name):
        print("[!] 모든 항목을 입력해야 합니다.")
        return
    
    if u_pw != u_pw_confirm:
        print("[!] 비밀번호가 일치하지 않습니다. 다시 시도해주세요.")
        return

    conn = get_connection()
    if not conn: return

    try:
        cursor = conn.cursor()
        sql = "INSERT INTO Users (user_id, user_pw, user_name) VALUES (:1, :2, :3)"
        cursor.execute(sql, [u_id, u_pw, u_name])
        conn.commit()
        print(f"{u_name}님, 회원가입 완료!")
    except oracledb.IntegrityError as e:
        error_obj, = e.args
        if error_obj.code == 1: # ORA-00001: Unique 제약 조건 위반 (아이디 중복)
            print("[!] 이미 존재하는 아이디입니다. 다른 아이디를 사용해주세요.")
        else:
            print(f"[!] 가입 실패: {error_obj.message}")
    finally:
        conn.close()

def login():
    print("\n--- 로그인 ---")
    u_id = input("아이디: ").strip()
    u_pw = getpass.getpass("비밀번호: ").strip()

    conn = get_connection()
    if not conn: return None

    try:
        cursor = conn.cursor()
        sql = "SELECT user_no, user_id, user_name FROM Users WHERE user_id = :1 AND user_pw = :2"
        cursor.execute(sql, [u_id, u_pw])
        row = cursor.fetchone()

        if row:
            is_admin = (u_id == 'admin')
            print(f"{row[2]}님 환영합니다!" + ("\n관리자 모드를 실행합니다." if is_admin else ""))
            return {"user_no": row[0], "user_id": row[1], "user_name": row[2], "is_admin": is_admin}
        else:
            print("[!] 아이디/비밀번호를 확인하세요.")
            return None
    finally:
        conn.close()
