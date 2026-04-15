import random

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