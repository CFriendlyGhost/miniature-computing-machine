import sqlite3

from flask import Flask, json, request, jsonify

app = Flask(__name__)


def create_database():
    connection = sqlite3.connect("bank.db")
    cursor = connection.cursor()
    cursor.execute("DROP TABLE transactions")
    cursor.execute("DROP TABLE accounts")
    cursor.execute(
        """ CREATE TABLE transactions (
                    transaction_id INTEGER primary key,
                    account_id INTEGER,
                    isDeposit INTEGER,
                    amount REAL,
                    FOREIGN KEY(account_id) REFERENCES accounts(account_id)
                    )"""
    )

    cursor.execute(
        """CREATE TABLE accounts (
                    account_id INTEGER primary key,
                    balance REAL
                    )"""
    )
    connection.commit()
    connection.close()


def insert_test_records():
    connection = sqlite3.connect("bank.db")
    cursor = connection.cursor()

    cursor.execute("INSERT INTO accounts VALUES(0, 1000)")
    cursor.execute("INSERT INTO accounts VALUES (1, 1000)")
    cursor.execute("INSERT INTO transactions VALUES (0, 0, 1, 1000)")
    cursor.execute("INSERT INTO transactions VALUES (1, 0, 1, 2000)")
    cursor.execute("INSERT INTO transactions VALUES (2, 0, 1, 2300)")
    cursor.execute("UPDATE accounts SET balance = 6300 WHERE account_id == 0")
    cursor.execute("INSERT INTO transactions VALUES (3, 1, 1, 1111)")
    cursor.execute("UPDATE accounts SET balance = 2111 WHERE account_id == 1")

    connection.commit()
    connection.close()


def create_new_account(account_id):
    connection = sqlite3.connect("bank.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO accounts VALUES(?, 1000)", (account_id,))
    connection.commit()
    connection.close()


def update_database(account_id, isDeposit, amount):
    connection = sqlite3.connect("bank.db")
    cursor = connection.cursor()
    is_transaction_successful = False

    cursor.execute("SELECT * FROM accounts WHERE account_id == ?", (account_id,))
    is_account_active = len(cursor.fetchall()) > 0

    if not is_account_active:
        create_new_account(account_id)

    if isDeposit:
        cursor.execute(
            "UPDATE accounts SET balance = balance + ? WHERE account_id == ?",
            (amount, account_id),
        )
        cursor.execute(
            "INSERT INTO transactions (account_id, isDeposit, amount) VALUES(?, ?, ?)",
            (account_id, 1, amount),
        )
        is_transaction_successful = True

    else:
        cursor.execute(
            "SELECT balance FROM accounts WHERE account_id == ?", (account_id,)
        )
        retrieved_amount = cursor.fetchall()
        if retrieved_amount[0][0] > amount:
            cursor.execute(
                "UPDATE accounts SET balance = balance - ? WHERE account_id == ?",
                (amount, account_id),
            )
            cursor.execute(
                "INSERT INTO transactions (account_id, isDeposit, amount) VALUES(?, ?, ?)",
                (account_id, 0, amount),
            )
            is_transaction_successful = True

    connection.commit()
    connection.close()
    return is_transaction_successful


@app.route("/bank/data/<int:accountId>", methods=["GET"])
def extract_records(accountId):
    if request.method == "GET":
        connection = sqlite3.connect("bank.db")
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * " "FROM accounts " "WHERE account_id == ?", (accountId,)
        )
        account = cursor.fetchall()

        if not account:
            connection.close()
            return json.dumps({"error": "Account not found"}), 404

        cursor.execute(
            "SELECT * " "FROM transactions " "WHERE account_id == ?", (accountId,)
        )
        transactions_records = cursor.fetchall()

        connection.close()

        account_dict = {"idKonta": account[0][0], "bilans": account[0][1]}

        transactions = [
            {
                "idTransakcji": record[0],
                "idKonta": record[1],
                "czyWplata": bool(record[2]),
                "stanKonta": record[3],
            }
            for record in transactions_records
        ]

        response = jsonify({"account": account_dict, "transactions": transactions})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response


if __name__ == "__main__":
    # create_database()
    # insert_test_records()
    # print(update_database(0, True, 1000))
    # print(update_database(0, False, 5300))
    # print(update_database(0, False, 1000))
    # print(update_database(1, False, 20000))
    # print(update_database(2, True, 1000000))
    app.run(debug=True)
