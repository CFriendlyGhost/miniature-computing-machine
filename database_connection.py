import sqlite3

from flask import Flask, json, request

app = Flask(__name__)


def create_database():
    connection = sqlite3.connect("bank.db")
    cursor = connection.cursor()
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
    cursor.execute("INSERT INTO transactions VALUES (0, 0, 300, 0)")
    cursor.execute("INSERT INTO transactions VALUES (2, 0, 300, 0)")
    cursor.execute("INSERT INTO transactions VALUES (3, 0, 300, 0)")
    cursor.execute("INSERT INTO transactions VALUES (1, 1, 350, 1)")

    connection.commit()
    connection.close()


@app.route('/bank/data/<int:accountId>', methods=['GET'])
def extract_records(accountId):
    if request.method == 'GET':
        connection = sqlite3.connect("bank.db")
        cursor = connection.cursor()

        cursor.execute("SELECT * "
                       "FROM accounts "
                       "WHERE account_id == ?", (accountId,))
        account = cursor.fetchall()

        if not account:
            connection.close()
            return json.dumps({"error": "Account not found"}), 404

        cursor.execute("SELECT * "
                       "FROM transactions "
                       "WHERE account_id == ?", (accountId,))
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

        return json.dumps({"account": account_dict, "transactions": transactions})


if __name__ == "__main__":
    # create_database()
    # insert_test_records()
    app.run(debug=True)

