import sqlite3
import datetime
import re


def establish_connection(file="phone_book.db"):
    conn = sqlite3.connect(file)
    cur = conn.cursor()
    return conn, cur


def safe_input(arg: str = ''):
    result = input(arg)
    return re.sub(r'[^a-zA-Z0-9-\.]', ' ', result)


def check_choose_correctness(choose, n1, n2):
    try:
        command = int(choose)
    except ValueError:
        print('You entered incorrect command.\n Please, choose a command from the list and enter its number '
              'without any other symbols')
        return False
    else:
        if command not in range(n1, n2 + 1):
            print(f'There is no such command.\nChoose command from {n1} to {n2}')
            return False
        return True


def handle_existing_person(name, surname, conn, cur):
    print('This person is already in your phonebook. Would you like to change the record?\n'
          'Enter yes or no')
    while True:
        command_change = safe_input().lower().strip()
        if command_change == 'yes':
            cur.execute(f"SELECT * FROM people WHERE Name='{name}' AND Surname='{surname}'")
            person = cur.fetchall()
            change_record(conn, cur, person)
        elif command_change == 'no':
            return
        else:
            print(f'I do not understand. Enter yes if to change the record of {name} {surname} '
                  'or no to leave as it is.\nWithout any symbols!')


def enter_birthdate():
    while True:
        birth_date_str = safe_input().strip()

        if birth_date_str == '0':
            return 0
        try:
            for symbol in birth_date_str.split('.'):
                int(symbol)
        except ValueError:
            print('Date should consist of numbers and dots only.')
            continue

        birth_date_list = birth_date_str.split('.')

        if len(birth_date_list) == 3:
            year = birth_date_list[2]
        else:
            print('The date is not correct. Try again. The format: DD.MM.YYYY'
                  '\nTry again or enter 0 to stop creating a new record')
            continue

        if len(year) == 4 and 1900 <= int(year) <= 2020:
            month = birth_date_list[1]
        else:
            print('Year is incorrect. It should contain 4 numbers from 1900 to 2020.'
                  '\nTry again or enter 0 to stop creating a new record')
            continue

        if len(month) <= 2 and 0 < int(month) <= 12:
            date = birth_date_list[0]
        else:
            print('Month is no correct. Enter a number from 01 to 12 on the second place.\n'
                  'Number of month should consist of two symbols. Examples: 01.10.1974\n       05.03.2001'
                  '\nTry again or enter 0 to stop creating a new record')
            continue

        if len(date) == 2 and ((month in ['03', '05', '07', '08', '10', '12'] and 1 <= int(date) <= 31) or
                               (month in ['01', '04', '06', '09', '11'] and 1 <= int(date) <= 31) or
                               (month == '02' and 1 <= int(date) <= 29)):
            return birth_date_str
        else:
            print('Month is not correct. Enter a number from 01 to 31 on the second place considering '
                  'number of days in each month.\nExamples: 31.12.2000\n          01.02.1999'
                  '\nTry again or enter 0 to stop creating a new record')
            continue


def enter_number():
    while True:
        number = safe_input().strip()

        if number == '0':
            return 0

        if number and number[0] in '78' and len(number) == 11:
            try:
                map(int, number)
            except ValueError:
                print('Phone number must contain only numbers. Try again.')
                continue
            else:
                number = '8' + number[1:]
        else:
            print('Incorrect number. It should contain 11 numbers and start with 7, +7 or 8')
            continue

        return number


def add_name_surname(conn, cur, name='', surname=''):
    if not name and not surname:
        name = safe_input('Enter name: ').capitalize().strip()
        surname = safe_input('Enter Surname: ').capitalize().strip()

    cur.execute(f"SELECT Name, Surname FROM people WHERE Name='{name}' AND Surname='{surname}'")
    people = cur.fetchall()
    if people:
        handle_existing_person(name, surname, conn, cur)
        return '-1', '-1'

    return name, surname


def count_age(birthday):
    birth_day, birth_month, birth_year = birthday.split('.')
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day

    if month > int(birth_month) or (month == int(birth_month) and day > int(birth_day)):
        return year - int(birth_year)

    return year - int(birth_year) - 1


def ask_birthday():
    while True:
        birthday_ask = safe_input('Do you want to enter birth date? [yes/no] ').strip().lower()
        if birthday_ask == 'yes':
            print('Enter person\'s birth date [DD.MM.YYYY]\nExample: 31.12.2000')
            birth_date = enter_birthdate()
            if birth_date:
                age = count_age(birth_date)
            else:
                age = '0'

        elif birthday_ask == 'no':
            birth_date = '0'
            age = '0'

        else:
            print('Incorrect answer. Enter yes or no.')
            continue
        return birth_date, age


def ask_number(cur):
    while True:
        print('Enter number: ', end='')
        number = enter_number()
        cur.execute(f"SELECT * FROM people WHERE Number='{number}'")
        people = cur.fetchall()
        if people:
            print(f'This number already belongs to {people[0][0]} {people[0][1]}.\n'
                  f'Enter another number to continue creating new record or enter 0 to quit')
            continue
        else:
            return number


def add_new_record(conn, cur):
    name, surname = add_name_surname(conn, cur)

    if not name and not surname:
        print('Name or Surname cannot be empty or contain not latin letters:(')
        return

    if name == '-1' or surname == '-1':
        return

    birth_date, age = ask_birthday()

    number = ask_number(cur)

    if number == 0:
        return

    cur.execute(f"""INSERT INTO people(Name, Surname, Number, Birthday, Age, Blocked) 
       VALUES('{name}', '{surname}', '{number}', '{birth_date}', '{age}', '0');""")
    conn.commit()

    print(f'\n=== New record was added successfully ===')
    print_person((name, surname, number, birth_date, age, '0'))


def print_person(person):
    print(f'Name: {person[0]} {person[1]}\nNumber: {person[2]}')

    if person[3] != '0':
        print(f'Birthday: {person[3]}\nAge: {person[4]}')

    if person[5] == '1':
        print('This person is blocked')
    print('=========================================\n')


def print_people(people):
    if isinstance(people, tuple) and people:
        print('=========================================')
        print_person(people)
        return

    if isinstance(people, list) and people:
        for ind, person in enumerate(people):
            print(f'№ {ind + 1} =====================================')
            print_person(person)

        return

    print('Not found. Try another way to search')
    return


def search_record(cur):
    while True:
        print("""How do you want to search?
    1. by name
    2. by surname
    3. by name and surname
    4. by number
    5. by birthday
    0. quit""")

        choose = safe_input().strip()

        is_correct_choose = check_choose_correctness(choose, 0, 5)
        if not is_correct_choose:
            continue

        if choose == '1':
            name = safe_input('Enter name: ').capitalize().strip()
            cur.execute(f"SELECT * FROM people WHERE Name='{name}'")

        elif choose == '2':
            surname = safe_input('Enter surname: ').capitalize().strip()
            cur.execute(f"SELECT * FROM people WHERE Surname='{surname}'")

        elif choose == '3':
            name = safe_input('Enter name: ').capitalize().strip()
            surname = safe_input('Enter surname: ').capitalize().strip()
            cur.execute(f"SELECT * FROM people WHERE Name='{name}' AND Surname='{surname}'")

        elif choose == '4':
            print('Enter number: ', end='')
            number = enter_number()
            cur.execute(f"SELECT * FROM people WHERE Number='{number}'")

        elif choose == '5':
            print('Enter person\'s birth date [DD.MM.YYYY]\nExample: 31.12.2000')
            print('Enter birthday: ', end='')
            birthday = enter_birthdate()
            cur.execute(f"SELECT * FROM people WHERE Birthday='{birthday}'")

        else:
            return ''

        people = cur.fetchall()
        print_people(people)

        if len(people):
            while True:
                print('Have you found the needed record?[yes/no] ', end='')
                found = safe_input().strip().lower()
                if found == 'yes':
                    return people
                elif found == 'no':
                    break
                else:
                    print('Incorrect command. Enter yes or no')


def delete_record(conn, cur):
    print('Find a record you want to delete.')
    people = search_record(cur)

    if len(people) > 1:
        while True:
            print(f'Which record do you want to delete? Enter the number from 1 to {len(people)}: ', end='')
            choose = safe_input()

            is_correct_choose = check_choose_correctness(choose, 1, len(people))
            if not is_correct_choose:
                continue
            break
    else:
        choose = 1

    print('Are you sure that you want to delete this record? [yes/no] ', end='')
    answer = safe_input().strip().lower()
    if answer == 'yes':
        person_ind = int(choose) - 1
        cur.execute(f"DELETE FROM people WHERE Name='{people[person_ind][0]}' AND Surname='{people[person_ind][1]}'")
        conn.commit()
        print('The record wad deleted successfully!')
        return
    else:
        print('Deletion was stopped.')
        return


def change_record(conn, cur, people=''):
    if not people:
        people = search_record(cur)

    if len(people) > 1:
        while True:
            print('Choose number of the record you want to change: ', end='')
            choose = safe_input()
            is_correct_choose = check_choose_correctness(choose, 1, len(people))
            if not is_correct_choose:
                continue
    elif len(people) == 1:
        person = people[0]
    else:
        return

    while True:
        print("""What do you want to change?
    1. Name
    2. Surname
    3. Number
    4. Birth date
    5. Block/Unblock the person
    0. quit""")

        choose = safe_input().strip()

        is_correct_choose = check_choose_correctness(choose, 0, 5)
        if not is_correct_choose:
            continue

        name = person[0]
        surname = person[1]

        if choose == '1':
            new_name = safe_input('Enter new name: ').strip().lower().capitalize()
            cur.execute(f"UPDATE people SET Name='{new_name}' WHERE Name='{name}' AND Surname='{surname}'")
            name = new_name

        elif choose == '2':
            new_surname = safe_input('Enter new surname: ').strip().lower().capitalize()
            cur.execute(f"UPDATE people SET Surname='{new_surname}' WHERE Name='{name}' AND Surname='{surname}'")
            surname = new_surname

        elif choose == '3':
            print('Enter new number: ', end='')
            new_number = enter_number()
            cur.execute(f"UPDATE people SET Number='{new_number}' WHERE Name='{name}' AND Surname='{surname}'")

        elif choose == '4':
            print('Enter new birth date: ', end='')
            new_birthdate = enter_birthdate()
            new_age = count_age(new_birthdate)
            cur.execute(f"UPDATE people SET Birthday='{new_birthdate}', Age='{new_age}'"
                        f"WHERE Name='{name}' AND Surname='{surname}'")

        elif choose == '5':
            cur.execute(f"SELECT Blocked FROM people WHERE Name='{name}' AND Surname='{surname}'")
            is_blocked = cur.fetchall()[0][0]

            if is_blocked == '1':
                cur.execute(f"UPDATE people SET Blocked='0' WHERE Name='{name}' AND Surname='{surname}'")
            else:
                cur.execute(f"UPDATE people SET Blocked='1' WHERE Name='{name}' AND Surname='{surname}'")

        conn.commit()
        cur.execute(f"SELECT * FROM people WHERE Name='{name}' AND Surname='{surname}'")
        new_person = cur.fetchall()

        print_people(new_person)

        while True:
            print('Do you want to make any other changes? [yes/no] ', end='')
            more_changes = safe_input().strip().lower()

            if more_changes == 'yes':
                break
            elif more_changes == 'no':
                return
            else:
                print('Incorrect input')


def show_nearest_birthdays(cur):
    now = datetime.datetime.now()
    day = now.day
    month = now.month
    cur.execute(f"SELECT * FROM people WHERE Birthday LIKE '__.{month}.____' OR Birthday LIKE '__.{month + 1}.____'")
    people = cur.fetchall()

    if people:
        for person in people:
            if int(person[3][3:5]) == month and int(person[3][:2]) < day:
                continue
            print('=========================================')
            print_person(person)
    else:
        print('No birthdays soon :(')
    return


def show_all_records(cur):
    cur.execute("SELECT * FROM people")
    people = cur.fetchall()
    print_people(people)
    return


def add_birthday_age(person, conn, cur):
    while True:
        print(f'I don\'t know {person[0]} {person[1]}\'s age.Would you like to add his/her birth date?[yes/no] ',
              end='')
        choose = input().lower().strip()
        if choose == 'yes':
            print('Enter birthdate: ', end='')
            birthday = enter_birthdate()
            age = count_age(birthday)
            cur.execute(f"UPDATE people SET Birthday='{birthday}', Age='{age}'"
                        f"WHERE Name='{person[0]}' AND Surname='{person[1]}'")
            conn.commit()
            print(f'{person[0]} {person[1]} is {age} years old')
            return
        elif choose == 'no':
            return
        else:
            print('Incorrect command.')


def show_age(cur, conn):
    print('Find a person to find out his/her age')
    people = search_record(cur)
    for person in people:
        if person[4] != 0:
            print(f'{person[0]} {person[1]} is {person[4]} years old')
        else:
            add_birthday_age(person, conn, cur)
            return
