from db_config import get_connection
from utils import print_all_users

def admin_menu():
    while True:
        print("\n=== [관리자 전용 메뉴] ===")
        print("1. 전체 사용자 조회\n2. 사용자 정보 수정 \n3. 사용자 삭제\n4. 이전 메뉴")
        choice = input("선택: ").strip()

        if choice == '1': list_all_users()
        elif choice == '2': update_user_info()
        elif choice == '3': delete_user()
        elif choice == '4': break

def list_all_users():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        sql = """
        SELECT user_no, user_id, user_name 
        FROM Users 
        WHERE is_admin = 0
        ORDER BY user_no DESC
        """
        cursor.execute(sql)
        users = cursor.fetchall()

        if not users:
            print("\n[!] 등록된 사용자가 없습니다.")
            return

        print_all_users(users)
        
    except Exception as e:
        print(f"[!] 사용자 목록 조회 중 오류가 발생했습니다: {e}")
    finally:
        conn.close()

def update_user_info():
    target_id = input("수정할 사용자의 ID: ").strip()

    if target_id.lower() == 'admin':
        print("[!] 관리자 계정은 수정할 수 없습니다.")
        return

    # TODO: 이름 변경은 고려해 보기
    new_name = input("새로운 이름(변경 없으면 엔터): ").strip()
    new_pw = input("새로운 비밀번호(변경 없으면 엔터): ").strip()

    conn = get_connection()
    try:
        cursor = conn.cursor()
        if new_name:
            cursor.execute("UPDATE Users SET user_name = :1 WHERE user_id = :2", [new_name, target_id])
        if new_pw:
            cursor.execute("UPDATE Users SET user_pw = :1 WHERE user_id = :2", [new_pw, target_id])
        
        conn.commit()
        print(f"{target_id} 사용자의 정보가 업데이트되었습니다.")
    finally:
        conn.close()

def delete_user():
    target_id = input("삭제할 사용자의 ID: ")

    if target_id.lower() == 'admin':
        print("[!] 관리자 계정은 삭제할 수 없습니다.")
        return

    confirm = input(f"[!] 정말로 {target_id} 사용자와 관련된 모든 데이터를 삭제하시겠습니까? (Y/N): ").strip()
    if confirm.upper() != 'Y': 
        print("삭제가 취소되었습니다.")
        return

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Users WHERE user_id = :1", [target_id])

        if cursor.rowcount == 0:
            print("[!] 해당 ID의 사용자를 찾을 수 없습니다.")
        else:
            conn.commit()
            print(f"[!] {target_id} 사용자가 성공적으로 삭제되었습니다.")

    except Exception as e:
        if conn: conn.rollback() # 오류 발생 시 원상 복구
        print(f"[!] 시스템 오류로 삭제에 실패했습니다: {e}")
    finally:
        conn.close()