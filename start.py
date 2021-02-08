import phone_book, sys

conn, cur = phone_book.establish_connection()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='people';")
table_exist = cur.fetchall()
if not table_exist:
    print('There is no such file :(\n'
          'Rename your phone book file like this: phone_book.db and move to the folder where'
          ' phone_book.py is.')
    sys.exit()


print('\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-='
      '\n=-=-=-Welcome to your phone book!-=-=-='
      '\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')

while True:
    print('''\nChoose action:
    1. Add new record to the phonebook 
    2. Search for a record
    3. Delete a record
    4. Change a record
    5. Show the nearest birthdays
    6. Show all records
    7. Show person's age
    0. quit
>>>''', end=' ')

    choose = input().strip()
    is_correct_choose = phone_book.check_choose_correctness(choose, 0, 7)

    if not is_correct_choose:
        continue

    if choose == '0':
        print('Bye!')
        break

    elif choose == '1':
        phone_book.add_new_record(conn, cur)

    elif choose == '2':
        phone_book.search_record(cur)

    elif choose == '3':
        phone_book.delete_record(conn, cur)

    elif choose == '4':
        print('Find the record you want to change')
        phone_book.change_record(conn, cur)

    elif choose == '5':
        print('People whose birthdays are this or next month:')
        phone_book.show_nearest_birthdays(cur)

    elif choose == '6':
        phone_book.show_all_records(cur)

    elif choose == '7':
        phone_book.show_age(cur, conn)
