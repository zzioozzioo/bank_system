import oracledb
from db_config import get_connection
from prettytable import PrettyTable

def create_account(user_session):

    print(f"\n--- {user_session['user_name']}님의 새 계좌 등록 ---")
    
    banks = ['하나은행', '우리은행', '국민은행', '신한은행', '기업은행']
    print(f"가능한 은행: {', '.join(banks)}")
    bank_name = input("은행명 입력: ")
    
    if bank_name not in banks:
        print("[!] 등록 가능한 은행이 아닙니다.")
        return

    account_num = input("계좌번호 입력(숫자만): ")
    if not account_num.isdigit():
        print("[!] 계좌번호는 숫자만 입력 가능합니다.")
        return
    
    alias = input("계좌 별칭: ")
    
    try:
        initial_deposit = int(input("최초 입금액(1,000원 이상): "))
        if initial_deposit < 1000:
            print("[!] 최초 생성 시 1,000원 이상 입금해야 합니다.")
            return
    except ValueError:
        print("[!] 숫자만 입력 가능합니다.")
        return

    conn = get_connection()
    if not conn: return

    try:
        cursor = conn.cursor()
        # owner_no에 로그인 세션의 user_no를 넣음으로써 소유자 연결
        sql = """
        INSERT INTO Accounts (account_num, bank_name, owner_no, balance, alias) 
        VALUES (:1, :2, :3, :4, :5)
        """
        cursor.execute(sql, [account_num, bank_name, user_session['user_no'], initial_deposit, alias])
        
        sql_log = """
        INSERT INTO Transactions (to_bank, to_acc, amount, t_type) 
        VALUES (:1, :2, :3, :4)
        """
        cursor.execute(sql_log, [bank_name, account_num, initial_deposit, '신규개설'])
        
        conn.commit()
        print(f"[!] {bank_name}({account_num}) 계좌가 등록되었습니다!")
    except oracledb.IntegrityError:
        print("[!] 유효하지 않은 계좌번호입니다.")
    finally:
        conn.close()

def get_my_accounts(user_session):
    while True:
        print("\n--- 계좌 관리 ---")
        print("1. 전체 계좌 조회")
        print("2. 계좌번호로 검색")
        print("3. 별칭으로 검색")
        print("4. 은행별 검색")
        print("5. 이전 메뉴")

        choice = input("조회 방식 선택: ").strip()

        if choice == '5': break

        sql = """
        SELECT account_num, bank_name, alias, balance FROM Accounts 
        WHERE owner_no = :1
        """
        params = [user_session['user_no']]

        # 검색 조건
        if choice == '2':
            search_val = input("검색할 계좌번호 입력: ").strip()
            sql += " AND account_num LIKE :2"
            params.append(f"%{search_val}%")
        elif choice == '3':
            search_val = input("검색할 별칭 입력: ").strip()
            sql += " AND alias LIKE :2"
            params.append(f"%{search_val}%")
        elif choice == '4':
            search_val = input("검색할 은행명 입력(하나, 우리, 국민, 신한, 기업): ").strip()

            if not search_val.endswith("은행"):
                search_val += "은행"

            sql += " AND bank_name LIKE :2"
            params.append(f"%{search_val}%")
        elif choice != '1':
            print("[!] 잘못된 선택입니다.")
            continue

        execute_account_search(sql, params)

def execute_account_search(sql, params):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()

        table = PrettyTable()
        table.field_names = ["계좌번호", "은행", "별칭", "잔액"]
        
        if not rows:
            print("\n[!] 조회된 계좌가 없습니다.")
        else:
            for row in rows:
                formatted_row = list(row)
                formatted_row[3] = f"{row[3]:,}원"
                table.add_row(formatted_row)
            
            table.align["계좌번호"] = "l"
            table.align["은행"] = "l"
            table.align["별칭"] = "l"
            table.align["잔액"] = "r"

            print(table)

    except Exception as e:
        print(f"[!] 조회 중 오류 발생: {e}")
    finally:
        conn.close()
    
def manage_account(user_session):
    while True:
        print(f"\n--- 계좌 관리 메뉴 ---")
        print("1. 계좌 수정")
        print("2. 계좌 삭제")
        print("3. 이전 메뉴")
        
        sub_choice = input("선택: ").strip()
        
        if sub_choice == '1':
            update_account(user_session)
        elif sub_choice == '2':
            delete_account(user_session)       
        elif sub_choice == '3':
            break
        else:
            print("[!] 잘못된 입력입니다.")

def update_account(user_session):
    print("\n--- 계좌 별칭 수정 ---")
    acc_num = input("수정할 계좌번호: ").strip()
    new_alias = input("새로운 별칭: ").strip()

    conn = get_connection()
    try:
        cursor = conn.cursor()
        # 본인의 계좌만 수정할 수 있도록 user_no 조건 포함
        sql = "UPDATE Accounts SET account_alias = :1 WHERE account_num = :2 AND user_no = :3"
        cursor.execute(sql, [new_alias, acc_num, user_session['user_no']])
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"계좌[{acc_num}]의 별칭이 '{new_alias}'(으)로 변경되었습니다.")
        else:
            print("[!] 해당 계좌를 찾을 수 없거나 수정 권한이 없습니다.")
    except Exception as e:
        print(f"[!] 수정 중 오류 발생: {e}")
    finally:
        conn.close()

def delete_account(user_session):
    print("\n--- 계좌 삭제 ---")
    acc_num = input("삭제할 계좌번호: ").strip()
    
    confirm = input(f"[!] 계좌[{acc_num}] 삭제 시 모든 거래 내역이 함께 사라집니다. 진행하시겠습니까? (Y/N): ")
    if confirm.upper() != 'Y':
        print("삭제가 취소되었습니다.")
        return

    conn = get_connection()
    try:
        cursor = conn.cursor()
        # 보안을 위해 본인 소유의 계좌인지 user_no로 다시 한번 확인 후 삭제
        sql = "DELETE FROM Accounts WHERE account_num = :1 AND user_no = :2"
        cursor.execute(sql, [acc_num, user_session['user_no']])
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"[!] 계좌[{acc_num}]가 성공적으로 삭제되었습니다.")
        else:
            print("[!] 계좌번호가 틀렸거나 삭제 권한이 없습니다.")
    except Exception as e:
        conn.rollback()
        print(f"[!] 삭제 중 오류 발생: {e}")
    finally:
        conn.close()