from auth import register, login
from admin import admin_menu
from account import create_account, get_my_accounts
from transaction import deposit_money, withdraw_money, transfer_money, get_transaction_history

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

# 사용자
# TODO: 계좌 별칭 수정 기능
# TODO: 계좌 생성, 등록, 수정, 삭제, 조회 기능
# TODO: 계좌번호로 계좌 정보 검색 기능
# TODO: 전체 계좌정보 리스트 검색 기능
# TODO: 별칭별, 계좌번호별, 은행별 계좌정보 리스트 검색

# 관리자
# TODO: 관리자 메뉴 생성 -> 사용자 정보 조회, 수정, 삭제
# TODO: DB에 관리자 계정 생성해두기