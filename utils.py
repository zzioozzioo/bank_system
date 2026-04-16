import random
from prettytable import PrettyTable

def generate_account_number(cursor, bank_name):
    bank_codes = {
        '하나은행': '001',
        '우리은행': '002',
        '국민은행': '003',
        '신한은행': '004',
        '기업은행': '005'
    }
    
    prefix = bank_codes.get(bank_name, '999') # 기본값 999
    
    product_code = "100" # 100으로 지정

    while True:
        serial_num = f"{random.randint(0, 999999):06d}"
        new_acc = f"{prefix}-{product_code}-{serial_num}"

        sql = "SELECT COUNT(*) FROM Accounts WHERE account_num = :1"
        cursor.execute(sql, [new_acc])
        count = cursor.fetchone()[0]

        if count == 0:
            return new_acc
        
from prettytable import PrettyTable

def print_all_users(users):
    table = PrettyTable()
    
    table.field_names = ["번호", "아이디", "이름", "계좌번호", "잔액"]

    for user in users:
        formatted_user = list(user)
        formatted_user[4] = f"{user[4]:,} 원"
        table.add_row(formatted_user)

    table.align["번호"] = "c"   
    table.align["아이디"] = "l"   
    table.align["이름"] = "l"      
    table.align["계좌번호"] = "l"  
    table.align["잔액"] = "r"     

    print(f"\n--- 사용자 목록 (총 {len(users)}명) ---")
    print(table)

def print_account_info(infos):
    table = PrettyTable()
    table.field_names = ["계좌번호", "은행", "별칭", "잔액"]
        
    if not infos:
        print("\n[!] 조회된 계좌가 없습니다.")
    else:
        for info in infos:
            formatted_info = list(info)
            formatted_info[3] = f"{info[3]:,}원"
            table.add_row(formatted_info)
            
        table.align["계좌번호"] = "l"
        table.align["은행"] = "l"
        table.align["별칭"] = "l"
        table.align["잔액"] = "r"

        print(table)

def print_transaction_history(histories):
    table = PrettyTable()
    table.field_names = ["거래일시", "유형", "금액", "상세 내용"]

    for history in histories:
        t_date, t_type, amount, f_bank, f_acc, t_bank, t_acc = history
            
        detail = ""
        if t_type == '입금':
                detail = f"[{t_bank}] {t_acc} 입금"
        elif t_type == '출금':
            detail = f"[{f_bank}] {f_acc} 출금"
        elif t_type in ['계좌이체', '타행이체출금', '타행이체입금']:
            detail = f"{f_acc} -> {t_acc}"
        elif t_type == '신규개설':
            detail = f"[{t_bank}] {t_acc} 신규 생성"
        else:
            detail = f"{t_type} 내역"

        table.add_row([t_date, t_type, f"{amount:,}원", detail])

    table.align["거래일시"] = "l"
    table.align["유형"] = "c"
    table.align["금액"] = "r"
    table.align["상세 내용"] = "l"

    print(table)

def validate_initial_deposit(initial_deposit):
    if initial_deposit < 1000:
        print("[!] 최초 생성 시 1,000원 이상 입금해야 합니다.")
        return False
    return True

def validate_amount(amount):
    if not isinstance(amount, (int, float)):
        print("[!] 숫자만 입력 가능합니다.")
        return False
        
    if amount < 1000:
        print("[!] 최소 1,000원 이상 입력해야 합니다.")
        return False
        
    return True

def validate_required_fields(u_id, u_pw, u_name):
    if not (u_id and u_pw and u_name):
        print("[!] 모든 항목을 입력해야 합니다.")
        return False
    return True

def validate_password(pw, pw_confirm):
    if pw != pw_confirm:
        print("[!] 비밀번호가 일치하지 않습니다. 다시 시도해주세요.")
        return False
    
    if len(pw) < 4:
        print("[WARN] 비밀번호는 최소 4자 이상이어야 합니다.")
        return False
    
    return True

def validate_balance(balance, amount):
    if balance < amount:
        print(f"[!] 잔액이 부족합니다. (현재 잔액: {balance:,}원)")
        return False
    return True

def confirm_delete_action(message):
    confirm = input(f"{message} (Y/N): ").strip().upper()
    return confirm == 'Y'

def add_bank_name(bank_name):
    if not bank_name.endswith("은행"):
        bank_name += "은행"
    return bank_name