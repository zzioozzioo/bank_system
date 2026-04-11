from auth import register, login
from account import create_account, get_my_accounts
from transaction import deposit_money, withdraw_money, transfer_money, get_transaction_history

def main_menu():
    while True:
        print("\n===== 통합계좌 관리시스템 =====")
        print("1. 회원가입")
        print("2. 로그인")
        print("3. 종료")
        print("==============================")
        
        choice = input("선택: ")
        
        if choice == '1':
            register()
        elif choice == '2':
            user_session = login()
            if user_session:
                bank_menu(user_session)
        elif choice == '3':
            print("프로그램을 종료합니다.")
            break

def bank_menu(user_session):
    while True:
        print(f"\n--- [{user_session['user_name']}]님의 은행 메뉴 ---")
        print("1. 내 계좌 생성")
        print("2. 내 계좌 조회")
        print("3. 입금")
        print("4. 출금")
        print("5. 계좌이체")
        print("6. 거래내역 조회")
        print("7. 로그아웃")
        
        choice = input("선택: ")
        if choice == '1':
            create_account(user_session)
        elif choice == '2':
            get_my_accounts(user_session)
        elif choice == '3':
            deposit_money(user_session)
        elif choice == '4':
            withdraw_money(user_session)
        elif choice == '5':
            transfer_money(user_session)
        elif choice == '6':
            get_transaction_history(user_session)
        elif choice == '7':
            print("로그아웃 되었습니다.")
            break
        else:
            # TODO: 기능 구현 후 추가
            print(f"'{choice}' 기능은 준비 중입니다.")

if __name__ == "__main__":
    main_menu()