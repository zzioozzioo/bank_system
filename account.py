import oracledb
from db_config import get_connection

def create_account(user_session):

    print(f"\n--- {user_session['user_name']}님의 새 계좌 등록 ---")
    
    # 1. 은행 선택 (요구사항 3번)
    banks = ['하나은행', '우리은행', '국민은행', '신한은행', '기업은행']
    print(f"가능한 은행: {', '.join(banks)}")
    bank_name = input("은행명 입력: ")
    
    if bank_name not in banks:
        print("❌ 등록 가능한 은행이 아닙니다.")
        return

    # 2. 정보 입력
    account_num = input("계좌번호 입력: ")
    alias = input("계좌 별칭(닉네임): ")
    
    # 3. 최초 입금액 체크 (요구사항 12번)
    try:
        initial_deposit = int(input("최초 입금액: "))
        if initial_deposit < 1000:
            # TODO: 1000원 미만일 경우 예외 처리(현재는 은행 메뉴로 나가버림)
            print("❌ 최초 생성 시 1,000원 이상 입금해야 합니다.")
            return
    except ValueError:
        print("❌ 숫자만 입력 가능합니다.")
        return

    # 4. DB 저장
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
        
        # 거래 내역에도 기록 (요구사항 9번 기초 데이터)
        sql_log = """
        INSERT INTO Transactions (to_bank, to_acc, amount, t_type) 
        VALUES (:1, :2, :3, :4)
        """
        cursor.execute(sql_log, [bank_name, account_num, initial_deposit, '신규개설'])
        
        conn.commit()
        print(f"✅ [{bank_name}] {account_num} 계좌가 등록되었습니다!")
    except oracledb.IntegrityError:
        print("❌ 이미 등록된 계좌번호이거나 중복된 별칭입니다.")
    finally:
        conn.close()

def get_my_accounts(user_session):

    def pad_korean(text, total_len):
        if text is None: text = ""
        k_count = 0
        for char in text:
            if ord('가') <= ord(char) <= ord('힣'): # 한글 범위 체크
                k_count += 1
        return text + ' ' * (total_len - len(text) - k_count)

    print(f"\n--- [{user_session['user_name']}]님의 보유 계좌 목록 ---")
    
    conn = get_connection()
    if not conn: return

    try:
        cursor = conn.cursor()
        # owner_no를 기준으로 해당 사용자의 계좌만 조회
        sql = """
        SELECT bank_name, account_num, alias, balance 
        FROM Accounts 
        WHERE owner_no = :1
        ORDER BY bank_name ASC
        """
        cursor.execute(sql, [user_session['user_no']])
        accounts = cursor.fetchall()

        if not accounts:
            print("❗ 등록된 계좌가 없습니다. 먼저 계좌를 생성해 주세요.")
            return

        # 결과 출력 (표 형식)
        h_bank = pad_korean("은행명", 14)
        h_acc = "계좌번호".ljust(13)
        h_alias = pad_korean("별칭", 16)
        h_bal = "잔액".rjust(12)
        
        print(f"{h_bank} | {h_acc} | {h_alias} | {h_bal}")
        print("-" * 75)
        
        for acc in accounts:
            # acc[0]:은행, [1]:계좌번호, [2]:별칭, [3]:잔액
            v_bank = pad_korean(acc[0], 14)
            v_acc = acc[1].ljust(17)
            v_alias = pad_korean(acc[2] if acc[2] else "(없음)", 16)
            v_bal = f"{acc[3]:,}원".rjust(12)
            
            print(f"{v_bank} | {v_acc} | {v_alias} | {v_bal}")
            
    except Exception as e:
        print(f"❌ 조회 중 오류 발생: {e}")
    finally:
        conn.close()

# TODO: 계좌 별칭 수정 기능
# TODO: 계좌 생성, 등록, 수정, 삭제, 조회 기능
# TODO: 계좌번호로 계좌 정보 검색 기능
# TODO: 전체 계좌정보 리스트 검색 기능
# TODO: 별칭별, 계좌번호별, 은행별 계좌정보 리스트 검색

# TODO: 관리자 메뉴 생성 -> 사용자 정보 조회, 수정, 삭제