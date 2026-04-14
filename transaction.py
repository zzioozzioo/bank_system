import oracledb
from db_config import get_connection

def deposit_money(user_session):
    print("\n--- 입금하기 ---")
    bank_name = input("은행명: ")
    account_num = input("입금할 계좌번호: ")
    try:
        amount = int(input("입금 금액: "))
        if amount <= 0:
            print("[!] 0원 이하의 금액은 입금할 수 없습니다.")
            return
    except ValueError:
        print("[!] 숫자만 입력 가능합니다.")
        return

    conn = get_connection()
    if not conn: return

    try:
        cursor = conn.cursor()
        # 1. 잔액 업데이트
        sql_update = """
        UPDATE Accounts SET balance = balance + :1 
        WHERE bank_name = :2 AND account_num = :3 AND owner_no = :4
        """
        cursor.execute(sql_update, [amount, bank_name, account_num, user_session['user_no']])
        
        if cursor.rowcount == 0:
            print("[!] [{bank_name}]에 해당 계좌번호가 없거나 본인 소유가 아닙니다.")
            return

        # 2. 거래내역 기록
        sql_log = """
        INSERT INTO Transactions (to_bank, to_acc, amount, t_type) VALUES (:1, :2, :3, :4)
        """
        cursor.execute(sql_log, [bank_name, account_num, amount, '입금'])
        
        conn.commit()
        print(f"{bank_name} {account_num} 계좌로 {amount:,}원 입금이 완료되었습니다.")
    except Exception as e:
        conn.rollback()
        print(f"[!] 오류 발생: {e}")
    finally:
        conn.close()

def withdraw_money(user_session):
    print("\n--- 출금하기 ---")
    bank_name = input("은행명: ")
    account_num = input("출금할 계좌번호: ")
    try:
        amount = int(input("출금 금액: "))
        if amount <= 0:
            print("[!] 0원 이하의 금액은 출금할 수 없습니다.")
            return
    except ValueError:
        print("[!] 숫자만 입력 가능합니다.")
        return

    conn = get_connection()
    if not conn: return

    try:
        cursor = conn.cursor()
        
        # 1. 잔액 확인 (조회)
        sql = """
        SELECT balance FROM Accounts 
        WHERE bank_name = :1 AND account_num = :2 AND owner_no = :3
        """
        cursor.execute(sql, [bank_name, account_num, user_session['user_no']])
        row = cursor.fetchone()
        
        if not row:
            print("[!] [{bank_name}]에 해당 계좌가 없거나 본인 소유가 아닙니다.")
            return
        
        current_balance = row[0]
        if current_balance < amount:
            print(f"[!] 잔액이 부족합니다. (현재 잔액: {current_balance:,}원)")
            return

        # 2. 잔액 업데이트
        sql_update = """
        UPDATE Accounts SET balance = balance - :1 
        WHERE bank_name = :2 AND account_num = :3
        """
        cursor.execute(sql_update, [amount, bank_name, account_num])

        # 3. 거래내역 기록
        sql_log = """
        INSERT INTO Transactions (from_bank, from_acc, amount, t_type) 
        VALUES (:1, :2, :3, :4)
        """
        cursor.execute(sql_log, [bank_name, account_num, amount, "출금"])
        
        conn.commit()
        print(f"{bank_name}({account_num}) 계좌에서 {amount:,}원 출금이 완료되었습니다.")
    except Exception as e:
        conn.rollback()
        print(f"[!] 오류 발생: {e}")
    finally:
        conn.close()

def transfer_money(user_session):
    print("\n--- 계좌이체 ---")

    from_bank = input("내 은행명: ")
    from_acc = input("내 계좌번호(출금): ")
    to_bank = input("상대방 은행명: ")
    to_acc = input("상대방 계좌번호(입금): ")
    
    try:
        amount = int(input("이체 금액: "))
        if amount <= 0:
            print("[!] 0원 이하의 금액은 이체할 수 없습니다.")
            return
    except ValueError:
        print("[!] 숫자만 입력 가능합니다.")
        return

    conn = get_connection()
    if not conn: return

    try:
        cursor = conn.cursor()
        
        # 내 계좌 잔액 확인 및 출금 가능 여부 체크
        sql_check = """
        SELECT balance FROM Accounts 
        WHERE bank_name = :1 AND account_num = :2 AND owner_no = :3
        """
        cursor.execute(sql_check, [from_bank, from_acc, user_session['user_no']])
        row = cursor.fetchone()
        
        if not row:
            print(f"[!] [{from_bank}] {from_acc} 계좌는 본인 소유가 아닙니다.")
            return
        
        if row[0] < amount:
            print(f"[!] 잔액이 부족합니다. (현재 잔액: {row[0]:,}원)")
            return

        # 내 계좌 출금
        sql_withdraw = """
        UPDATE Accounts SET balance = balance - :1 
        WHERE bank_name = :2 AND account_num = :3
        """
        cursor.execute(sql_withdraw, [amount, from_bank, from_acc])
        
        # 상대방 계좌 입금
        sql_deposit = """
        UPDATE Accounts SET balance = balance + :1 
        WHERE bank_name = :2 AND account_num = :3
        """
        cursor.execute(sql_deposit, [amount, to_bank, to_acc])
        
        if cursor.rowcount == 0:
            print("[!] [{to_bank}] {to_acc}는 존재하지 않는 계좌입니다. 이체를 취소합니다.")
            conn.rollback() # 상대방 계좌가 없으면 내 돈 깎인 것도 취소
            return

        # 거래내역 기록 (순서: 보낸은행, 보낸계좌, 받는은행, 받는계좌, 금액)
        sql_log = """
        INSERT INTO Transactions (from_bank, from_acc, to_bank, to_acc, amount, t_type) 
        VALUES (:1, :2, :3, :4, :5, '계좌이체')
        """
        cursor.execute(sql_log, [from_bank, from_acc, to_bank, to_acc, amount])
        
        # 모든 작업이 성공했을 때만 확정
        conn.commit()
        print(f"{amount:,}원을 {to_bank}({to_acc}) 계좌로 성공적으로 이체했습니다.")
        
    except Exception as e:
        conn.rollback() # 하나라도 오류 나면 전체 취소
        print(f"[!] 이체 중 오류 발생: {e}")
    finally:
        conn.close()

def transfer_to_friend(user_session):
    print("\n--- [타행 계좌이체] ---")

    my_bank = input("내 은행명: ").strip()
    if not my_bank.endswith("은행"): my_bank += "은행"
    my_acc = input("내 계좌번호: ").strip()

    friend_acc = input("상대방 계좌번호: ").strip()
    amount = int(input("이체 금액: "))

    my_conn = get_connection()
    
    friend_db_info = {
        'user': 'c##bank', # 상대방 아이디
        'password': 'bank', # 상대방 비밀번호
        'dsn': '172.31.57.146:1521/FREE' # 상대방 IP 주소
    }
    
    try:
        friend_conn = oracledb.connect(
            user=friend_db_info['user'], 
            password=friend_db_info['password'], 
            dsn=friend_db_info['dsn']
        )
        
        my_cursor = my_conn.cursor()
        friend_cursor = friend_conn.cursor()

        # 내 계좌 잔액 확인 및 출금
        my_sql = """
                SELECT balance FROM Accounts 
                WHERE bank_name = :1 AND account_num = :2 AND owner_no = :3        
        """
        my_cursor.execute(my_sql, [my_bank, my_acc, user_session['user_no']])
        result = my_cursor.fetchone()

        if not result:
            print(f"[!] 입력하신 {my_bank}의 {my_acc} 계좌를 찾을 수 없습니다.")
            return

        my_balance = result[0]
        if my_balance < amount:
            print(f"[!] 잔액이 부족합니다. (현재 잔액: {my_balance:,}원)")
            return
        
        # 내 DB 출금
        sql_withdraw = """
        UPDATE Accounts SET balance = balance - :1 WHERE bank_name = :2 AND account_num = :3
        """
        my_cursor.execute(sql_withdraw, [amount, my_bank, my_acc])

        # 상대방 DB 입금
        friend_sql = """
                    UPDATE Accounts SET balance = balance + :1 WHERE account_number = :2
        """
        friend_cursor.execute(friend_sql, [amount, friend_acc])

        if friend_cursor.rowcount == 0:
            raise Exception("[!] 상대방 계좌번호가 존재하지 않습니다.")
        
        # 출금 내역 기록 추가
        my_log_sql = """
            INSERT INTO Transactions (from_acc, to_acc, amount, t_type) 
            VALUES (:1, :2, :3, '타행이체출금')
        """
        my_cursor.execute(my_log_sql, [my_acc, friend_acc, amount])

        # 양쪽 DB 모두 확정
        my_conn.commit()
        friend_conn.commit()
        print(f"[!] {friend_acc}님께 {amount}원 이체 완료!")

    except Exception as e:
        # 중간에 에러난 경우 양쪽 다 취소
        my_conn.rollback()
        if 'friend_conn' in locals():
            friend_conn.rollback()
        print(f"[!] 이체 실패: {e}")
        
    finally:
        my_conn.close()
        if 'friend_conn' in locals():
            friend_conn.close()

def get_transaction_history(user_session):
    # TODO: 공통 함수 빼기
    def pad_korean(text, total_len):
        k_count = 0
        for char in text:
            if ord('가') <= ord(char) <= ord('힣'): # 한글 범위 체크
                k_count += 1
        return text + ' ' * (total_len - len(text) - k_count)


    print(f"\n--- [{user_session['user_name']}]님의 거래 내역 ---")
    
    conn = get_connection()
    if not conn: return

    try:
        cursor = conn.cursor()
        sql = """
        SELECT TO_CHAR(t_date, 'YYYY-MM-DD HH24:MI'), t_type, amount, 
               from_bank, from_acc, to_bank, to_acc
        FROM Transactions
        WHERE from_acc IN (SELECT account_num FROM Accounts WHERE owner_no = :1)
           OR to_acc IN (SELECT account_num FROM Accounts WHERE owner_no = :1)
        ORDER BY t_date ASC
        """
        cursor.execute(sql, [user_session['user_no'], user_session['user_no']])
        rows = cursor.fetchall()

        if not rows:
            print("[!] 거래 내역이 존재하지 않습니다.")
            return

        header_date = "날짜".ljust(16)
        header_type = pad_korean("유형", 10)
        header_amt = "금액".rjust(11)
        print(f"{header_date} | {header_type} | {header_amt} | 상세 내용")
        print("-" * 85)

        for row in rows:
            t_date, t_type, amount, f_bank, f_acc, t_bank, t_acc = row
            
            detail = ""
            if t_type == '입금':
                detail = f"[{t_bank}] {t_acc} 계좌로 입금"
            elif t_type == '출금':
                detail = f"[{f_bank}] {f_acc} 계좌에서 출금"
            elif t_type == '계좌이체':
                detail = f"[{f_bank}] {f_acc} -> [{t_bank}] {t_acc}"
            elif t_type == '신규개설':
                bank_info = f"[{t_bank}] " if t_bank else ""
                detail = f"{bank_info}{t_acc} 계좌 신규 생성"
            else:
                detail = f"{t_type} 내역"

            v_date = t_date.ljust(18)
            v_type = pad_korean(t_type, 10) 
            v_amt = f"{amount:,}원".rjust(12)
            print(f"{v_date} | {v_type} | {v_amt} | {detail}")

    except Exception as e:
        print(f"[!] 조회 중 오류 발생: {e}")
    finally:
        conn.close()