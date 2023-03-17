import socket
import pyodbc

# DESKTOP-QH4FU0U\SQLEXPRESS - database address
# Define ip and port and connection to database
timeout = 15
max_Retries = 3
client_Port = 30175
ip = "127.0.0.1"
server_Port = 20159
max_Size = 1024


# Database connection settings
DB_DRIVER = '{SQL Server}'
DB_SERVER = 'localhost'
DB_NAME = 'project'
DB_TRUSTED_CONNECTION = 'yes'

# Prints all the worker names in the table
def print_workers(connection):
    cursor = connection.cursor()
    output_str = "Workers list:\n"
    cursor.execute('SELECT [FirstName] FROM Workers')
    for row in cursor:
        output_str += str(row[0]) + "\n"
    connection.commit()
    return output_str


# Prints all the worker details sorted by their last name
def print_workers_sorted(connection):
    cursor = connection.cursor()
    output_str = "Sorted workers list:\n"
    cursor.execute("SELECT CAST([FirstName] as varchar(max)) as [First Name], CAST([LastName] as varchar(max)) as ["
                   "LastName], [ID], [WorkerID], [Salary] FROM Workers ORDER BY [LastName]")
    for row in cursor:
        output_str += str(row) + "\n"
    connection.commit()
    return output_str


# Adds a new worker to the table
def add_worker(connection):
    cursor = connection.cursor()
    first_Name = input("[SQL] Ennter new worker's first name:")
    last_Name = input("[SQL] Ennter new worker's last name:")
    id = input("[SQL] Enter new worker's ID:")
    w_Id = input("[SQL] Ennter new worker's work ID:")
    salary = input("[SQL] Ennter new worker's salary:")
    cursor.execute('insert into Workers([FirstName], [LastName], ID, [WorkerID], Salary) values(?,?,?,?,?);',
                   (first_Name, last_Name, id, w_Id, salary))
    connection.commit()
    print("[SQL] Worker added successfully!")


# Removes a worker from the table by work ID
def remove_worker(connection):
    cursor = connection.cursor()
    work_Id = input("[SQL] Enter worker's work ID:")
    cursor.execute(f"DELETE FROM Workers WHERE [WorkerID] = '{work_Id}'")
    print("[SQL] Worker removed successfully!")
    connection.commit()


# Prints a specific worker's details by his work ID
def get_worker_details(connection):
    cursor = connection.cursor()
    work_Id = input("[SQL] Enter worker's work ID:")
    cursor.execute('SELECT * FROM Workers WHERE [WorkerID] = 'f'{work_Id}')
    output_str = ""
    for row in cursor:
        output_str += str(row) + "\n"
    connection.commit()
    return output_str


# Prints the details for the first given amount of workers
def get_first_n_workers_details(connection):
    cursor = connection.cursor()
    num = input("[SQL] Enter the amount of first workers you wish to get their details: ")
    cursor.execute((f"SELECT TOP {num} * FROM Workers"))
    output_str = ""
    for row in cursor:
        output_str += str(row) + "\n"
    connection.commit()
    return output_str


# Updates a worker's salary
def update_worker_salary(connection):
    cursor = connection.cursor()
    work_Id = input("[SQL] Enter worker's work ID:")
    new_Salary = input("[SQL] Enter the new salary:")
    query = f"UPDATE Workers SET Salary = {new_Salary} WHERE [WorkerID] = '{work_Id}'"
    cursor.execute(query)
    print("[SQL] Salary updated successfully!")
    connection.commit()


# Counts the amount of the workers in the table and prints the result

def count_workers(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Workers")
    count = cursor.fetchone()[0]
    output_str = f"There are currently {count} workers in the table."
    connection.commit()
    return output_str


# Counts the amount of workers with a given salary and prints the result
def count_workers_with_given_salary(connection):
    cursor = connection.cursor()
    salary = input("[SQL] Enter salary: ")
    cursor.execute("SELECT COUNT(*) FROM Workers WHERE [Salary] = ?", salary)
    count = cursor.fetchone()[0]
    output_str = ""
    if count > 0:
        output_str = f"there are {count} workers with such salary"
    else:
        output_str = "there are not workers with such salary"
    connection.commit()
    return output_str


# Given a name, Prints all workers with that name and their details
def check_worker_exists(connection):
    cursor = connection.cursor()
    name = input("[SQL] Enter the name of the worker you are looking for: ")
    cursor.execute("SELECT * FROM Workers WHERE CAST([FirstName] as varchar(max)) = ?", name)
    output_str = f"Here is a list of workers that their name is: {name}:\n"
    for row in cursor:
        output_str += str(row) + "\n"
    connection.commit()
    return output_str


# Establish TCP connection between the client and this SQL server
def tcp_connection():
    # Create a TCP socket to connect to the client
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip, server_Port))
    sock.listen(1)
    print("[SQL] SQL Server is starting...")

    while True:
        client, address = sock.accept()
        print(f"[SQL] Connected to the client - {address[0]}:{address[1]}")

        # Send list of queries to the client
        list_of_Queries = "list of queries: \nprint workers\nprint workers sorted\nadd worker\nremove worker\nget " \
                          "worker details\nget " \
                          "first n workers details\nupdate worker salary\ncount workers\ncount workers with given " \
                          "salary\ncheck worker exists\n "
        client.send(bytes(list_of_Queries, "utf-8"))

        # Receive query name from the client and execute it
        while True:
            desired_Query = client.recv(max_Size)
            desired_Query.decode("utf-8")
            print(f"[SQL] Received from client {address}: {desired_Query}")
            if desired_Query == b"print workers":
                client.send(bytes(print_workers(connection), "utf-8"))
            elif desired_Query == b"print workers sorted":
                client.send(bytes(print_workers_sorted(connection), "utf-8"))
            elif desired_Query == b"add worker":
                add_worker(connection)
                client.send(bytes("Worker added successfully", "utf-8"))
            elif desired_Query == b"remove worker":
                remove_worker(connection)
                client.send(bytes("Worker removed successfully", "utf-8"))
            elif desired_Query == b"get worker details":
                client.send(bytes(get_worker_details(connection), "utf-8"))
            elif desired_Query == b"get first n workers details":
                client.send(bytes(get_first_n_workers_details(connection), "utf-8"))
            elif desired_Query == b"update worker salary":
                update_worker_salary(connection)
                client.send(bytes("Successfully updated salary!", "utf-8"))
            elif desired_Query == b"count workers with given salary":
                client.send(bytes(count_workers_with_given_salary(connection), "utf-8"))
            elif desired_Query == b"check worker exists":
                client.send(bytes(check_worker_exists(connection), "utf-8"))
            elif desired_Query == b"count workers":
                client.send(bytes(count_workers(connection), "utf-8"))
            elif desired_Query == b"nothing":
                print("[SQL] Client chose to stop sending queries")
                client.close()
                break
            else:
                print("[SQL] Query entered doesn't exist")
                client.send(bytes("Invalid query", "utf-8"))


# Reliable send from server to client
def reliable_send(sock, data, address):
    retries = 0
    ack_received = False
    while not ack_received and retries < max_Retries:
        sock.settimeout(timeout)
        sock.sendto(data, address)
        sock.settimeout(timeout)
        try:
            ack, _ = sock.recvfrom(max_Size)
            if ack == b"ACK":
                ack_received = True
        except socket.timeout:
            retries += 1
            sock.settimeout(timeout)
    if not ack_received:
        print("[SQL] No response received.")
        print("[SQL] Closing the connection...")
        sock.close()
        exit()


# Establish RUDP connection between the server and the client
def RUDP_Connection():
    # Create a UDP socket to connect to the client
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, server_Port))
    print("[SQL] SQL Server is starting...")

    # Receive initial message from the client
    data, address = sock.recvfrom(max_Size)
    print(f"[SQL] Received from client {address}: {data.decode('utf-8')}")

    # Send list of queries to the client
    queries = "List of queries: \nprint workers\nprint workers sorted\nadd worker\nremove worker\nget worker " \
              "details\nget first n workers details\nupdate worker salary\ncount workers\ncount workers with given " \
              "salary\ncheck worker exists\n "
    reliable_send(sock, queries.encode('utf-8'), address)
    print("[SQL] Sent list of queries to the client")
    count_Timeouts = 1
    received_queries = set()  # Will be used to check if we receive duplicate requests

    # Receive query name from the client and execute it
    while True:
        try:
            sock.settimeout(timeout)
            data, address = sock.recvfrom(max_Size)
            data = data.decode('utf-8')
            if data != "ACK":
                count_Timeouts = 1
                print(f"[SQL] Received from client {address}: {data}")
                if data in received_queries:  # Received the same query with same serial number
                    print("[SQL] Duplicate request detected")
                if data not in received_queries:
                    received_queries.add(data)
                    sock.sendto("ACK".encode("utf-8"), (ip, client_Port))
                    desired_Query = data.split("|")[0]
                    print(desired_Query)
                    if "print workers sorted" == desired_Query:
                        query_Result = print_workers_sorted(connection)
                        reliable_send(sock, query_Result.encode("utf-8"), address)
                    elif "print workers" == desired_Query:
                        query_Result = print_workers(connection)
                        reliable_send(sock, query_Result.encode("utf-8"), address)
                    elif "add worker" == desired_Query:
                        add_worker(connection)
                        query_Result = "Worker added successfully"
                        reliable_send(sock, query_Result.encode("utf-8"), address)
                    elif "remove worker" == desired_Query:
                        remove_worker(connection)
                        query_Result = "Worker removed successfully"
                        reliable_send(sock, query_Result.encode("utf-8"), address)
                    elif "get worker details" == desired_Query:
                        query_Result = get_worker_details(connection)
                        reliable_send(sock, query_Result.encode("utf-8"), address)
                    elif "get first n workers details" == desired_Query:
                        query_Result = get_first_n_workers_details(connection)
                        reliable_send(sock, query_Result.encode("utf-8"), address)
                    elif "update worker salary" == desired_Query:
                        update_worker_salary(connection)
                        query_Result = "Successfully updated salary!"
                        reliable_send(sock, query_Result.encode("utf-8"), address)
                    elif "count workers with given salary" == desired_Query:
                        query_Result = count_workers_with_given_salary(connection)
                        reliable_send(sock, query_Result.encode("utf-8"), address)
                    elif "check worker exists" == desired_Query:
                        query_Result = check_worker_exists(connection)
                        reliable_send(sock, query_Result.encode("utf-8"), address)
                    elif "count workers" == desired_Query:
                        query_Result = count_workers(connection)
                        reliable_send(sock, query_Result.encode("utf-8"), address)
                    elif "nothing" == desired_Query:
                        query_Result = "Closing connection"
                        reliable_send(sock, query_Result.encode("utf-8"), address)
                        print("[SQL] Client chose to stop sending requests, closing server...")
                        break
                    else:  # Case that an invalid query was entered by the client
                        query_Result = "invalid query"
                        reliable_send(sock, query_Result.encode("utf-8"), address)
                        print("[SQL] Query entered doesn't exist")
        except socket.timeout:  # Timeout waiting for a query, after 3 timeouts the server will shut down
            print(f"[SQL] Timeout #{count_Timeouts} while waiting for query")
            count_Timeouts += 1
            if count_Timeouts == 4:
                sock.sendto("Timed out".encode("utf-8"), (ip, client_Port))
                sock.sendto("query result = null".encode("utf-8"), (ip, client_Port))
                print("[SQL] Stopped receiving requests from client, closing server...")
                break
    sock.close()


if __name__ == '__main__':

    print("\n    SQL Server;  Copyright (C) 2023  Roy Simanovich and Yuval Yurzdichinsky\n"
		 "This program comes with ABSOLUTELY NO WARRANTY.\n"
		 "This is free software, and you are welcome to redistribute it\n"
		 "under certain conditions; see `LICENSE' for details.\n\n")

    try:
        # Connect to the database
        connection = pyodbc.connect('DRIVER=' + DB_DRIVER + ';SERVER='+ DB_SERVER +';DATABASE=' + DB_NAME + ';Trusted_connection=' + DB_TRUSTED_CONNECTION + ';')

        print("Choose which protocol you want to use:")
        print("1. TCP Connection")
        print("2. RUDP Connection")

        choice = input("Enter your choice: ")

        match choice:
            case '1':
                # Starts the SQL server, TCP connection
                tcp_connection()

            case '2':
                # Starts the SQL server, RUDP connection
                RUDP_Connection()

            case _:
                print("Invalid choice. Exiting...")

    except pyodbc.Error as ex:
        sqlstate = ex.args[1]
        print(sqlstate)

