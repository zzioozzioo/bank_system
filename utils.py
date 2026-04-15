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
        

def print_all_users(users):
    table = PrettyTable()
    
    table.field_names = ["번호", "아이디", "이름"]

    for user in users:
        table.add_row(user)

    table.align["번호"] = "c"
    table.align["아이디"] = "l"
    table.align["이름"] = "l"

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
            table.add_info(formatted_info)
            
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

        table.add_history([t_date, t_type, f"{amount:,}원", detail])

    table.align["거래일시"] = "l"
    table.align["유형"] = "c"
    table.align["금액"] = "r"
    table.align["상세 내용"] = "l"

    print(table)