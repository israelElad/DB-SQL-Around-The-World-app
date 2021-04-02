import mysql.connector.errors as errors

"""Not used anymore, kept as archive
"""

# def execute_sql_file(cursor, filename):
#     with open(filename, 'r') as f:
#         sql_file = f.read()

#     sql_commands = sql_file.split(';')

#     for command in sql_commands:
#         try:
#             cursor.execute(command)
#         except errors.OperationalError as error:
#             print("Command skipped: " + error)