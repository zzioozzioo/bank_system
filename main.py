from auth import register, login
from admin import admin_menu
from account import create_account, get_my_accounts, manage_account
from transaction import deposit_money, withdraw_money, transfer_money, transfer_to_friend, get_transaction_history

def main_menu():

    while True:
        print("\n===== 통합계좌 관리시스템 =====")
        print("1. 회원가입")
        print("2. 로그인")
        print("3. 종료")
        print("==============================")
        
        choice = input("선택: ").strip()
        
        if choice == '1':
            register()
        elif choice == '2':
            user_session = login()

            if user_session:
                if user_session['is_admin']:
                    admin_menu()
                else: 
                    bank_menu(user_session)

        elif choice == '3':
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 입력입니다. 다시 선택해 주세요.")

def bank_menu(user_session):
    while True:
        print(f"\n--- [{user_session['user_name']}]님의 은행 메뉴 ---")
        print("1. 내 계좌 생성")
        print("2. 내 계좌 조회")
        print("3. 내 계좌 관리")
        print("4. 입금")
        print("5. 출금")
        print("6. 계좌이체")
        print("7. 타행계좌이체")
        print("8. 거래내역 조회")
        print("9. 로그아웃")
        
        choice = input("선택: ")
        if choice == '1':
            create_account(user_session)
        elif choice == '2':
            get_my_accounts(user_session)
        elif choice == '3':
            manage_account(user_session)
        elif choice == '4':
            deposit_money(user_session)
        elif choice == '5':
            withdraw_money(user_session)
        elif choice == '6':
            transfer_money(user_session)
        elif choice == '7':
            transfer_to_friend(user_session)
        elif choice == '8':
            get_transaction_history(user_session)
        elif choice == '9':
            print("로그아웃 되었습니다.")
            break
        else:
            print(f"1~9번 메뉴 중에 선택해 주세요.")

if __name__ == "__main__":
    main_menu()