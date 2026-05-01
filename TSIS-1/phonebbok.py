import csv
from connect import connect
import json

conn = connect()
cur = conn.cursor()

def insert_from_csv():
    with open("contacts.csv", "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            cur.execute(
                "SELECT id FROM groups WHERE name=%s",
                (row["group_name"],)
            )
            group = cur.fetchone()

            if group:
                group_id = group[0]
            else:
                cur.execute(
                    "INSERT INTO groups(name) VALUES(%s) RETURNING id",
                    (row["group_name"],)
                )
                group_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO contacts(name,email,birthday,group_id)
                VALUES(%s,%s,%s,%s)
                ON CONFLICT(name) DO NOTHING
                RETURNING id
            """, (
                row["name"],
                row["email"],
                row["birthday"],
                group_id
            ))

            contact = cur.fetchone()

            if contact:
                contact_id = contact[0]
            else:
                cur.execute(
                    "SELECT id FROM contacts WHERE name=%s",
                    (row["name"],)
                )
                contact_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO phones(contact_id,phone,type)
                VALUES(%s,%s,%s)
            """, (
                contact_id,
                row["phone"],
                row["phone_type"]
            ))

    conn.commit()

def insert_from_console():
    name = input("Name: ")
    email = input("Email: ")
    birthday = input("Birthday (YYYY-MM-DD): ")
    group_name = input("Group: ")
    phone = input("Phone: ")
    phone_type = input("Phone type(home/work/mobile): ")

    cur.execute(
        "SELECT id FROM groups WHERE name=%s",
        (group_name,)
    )

    group = cur.fetchone()

    if group:
        group_id = group[0]
    else:
        cur.execute(
            "INSERT INTO groups(name) VALUES(%s) RETURNING id",
            (group_name,)
        )
        group_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO contacts(name,email,birthday,group_id)
        VALUES(%s,%s,%s,%s)
        RETURNING id
    """, (name,email,birthday,group_id))

    contact_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO phones(contact_id,phone,type)
        VALUES(%s,%s,%s)
    """, (contact_id,phone,phone_type))

    conn.commit()

def update_contact():
    name = input("Enter name to update: ")
    new_phone = input("Enter new phone: ")

    cur.execute("""
        UPDATE phones
        SET phone = %s
        WHERE contact_id = (
            SELECT id FROM contacts WHERE name = %s
        )
    """, (new_phone, name))

    conn.commit()
    print("Updated successfully")

def query_contacts():
    cur.execute("""
        SELECT c.name, c.email, c.birthday,
               g.name, p.phone, p.type
        FROM contacts c
        JOIN groups g ON c.group_id = g.id
        JOIN phones p ON c.id = p.contact_id
    """)

    for row in cur.fetchall():
        print(row)

def delete_contact():
    name = input("Enter name: ")

    cur.execute(
        "DELETE FROM contacts WHERE name=%s",
        (name,)
    )

    conn.commit()

def export_json():
    cur.execute("""
        SELECT c.name,c.email,c.birthday,
               g.name,p.phone,p.type
        FROM contacts c
        JOIN groups g ON c.group_id=g.id
        JOIN phones p ON c.id=p.contact_id
    """)

    data = cur.fetchall()

    with open("contacts.json","w") as f:
        json.dump(data,f,default=str)

    print("Exported")

def filter_by_group():
    group_name = input("Enter group: ")

    cur.execute("""
        SELECT c.name
        FROM contacts c
        JOIN groups g ON c.group_id=g.id
        WHERE g.name=%s
    """,(group_name,))

    print(cur.fetchall())

def main():
    while True:
        print("""
1.Insert CSV
2.Insert Console
3.Query
4.Delete
5.Filter Group
6.Export JSON
7.Update Contact
8.Exit
""")

        choice = input("Choose: ")

        if choice == "1":
            insert_from_csv()
        elif choice == "2":
            insert_from_console()
        elif choice == "3":
            query_contacts()
        elif choice == "4":
            delete_contact()
        elif choice == "5":
            filter_by_group()
        elif choice == "6":
            export_json()
        elif choice == "7":
            update_contact()
        elif choice == "8":
            break
        else:
            print("Invalid choice.")

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()