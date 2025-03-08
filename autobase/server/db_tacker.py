import mysql.connector

# Database credentials
db_config = {
    'host': 'localhost',
    'user': 'ixtar',
    'password': 'capstone123',
    'database': 'AUTOBASE',
}

SENSOR_STREAM_TABLE = "SENSOR_DATA"
WET_EVENT_TABLE = "ONGOING_WET_EVENT"
HISTORY_TABLE = "HISTORY"

class DataTracker():
    def get_last_data_entry(self):
        try:
            connection = mysql.connector.connect(**db_config)
            # Create a cursor object to interact with the database
            cursor = connection.cursor()

            # Example SELECT query to get the last entry ordered by timestamp
            query = f"SELECT * FROM {SENSOR_STREAM_TABLE} ORDER BY timestamp DESC LIMIT 1"

            # Execute the query
            cursor.execute(query)

            # Fetch the last entry : lools like
            """{
            "timestamp": "2023-11-13 02:01:08",
            "temperature": 23,
            "soil_moisture": 2.4,
            "rain_level": 4
            },"""

            last_data_entry = cursor.fetchall()

            if last_data_entry:
                for row in last_data_entry:
                    print(row)

                last_data_entry = last_data_entry[0]
                last_entry = {
                    "timestamp": last_data_entry[0],
                    "temperature": last_data_entry[1],
                    "soil_moisture": last_data_entry[2],
                    "rain_level": last_data_entry[3]
                    }
                
                return last_entry
            else:
                print("No rows found")

        finally:
            # Close the cursor and connection
            cursor.close()
            connection.close()
    
    def is_there_ongoing_wet_event(self):
        # Establish a connection to the MariaDB server
        connection = mysql.connector.connect(**db_config)

        try:
            # Create a cursor to interact with the database
            cursor = connection.cursor()

            # Execute a SELECT query to count the number of rows in the table
            query = f"SELECT COUNT(*) FROM {WET_EVENT_TABLE}"
            cursor.execute(query)

            # Fetch the result
            result = cursor.fetchone()

            # Check if the count is zero, indicating the table is empty
            if result[0] == 0:
                return False
            else: 
                return True

        finally:
            # Close the cursor and the connection
            cursor.close()
            connection.close()


    def get_wet_event_values(self):
        try:
            connection = mysql.connector.connect(**db_config)
            # Create a cursor object to interact with the database
            cursor = connection.cursor()

            # Example SELECT query to get the last entry ordered by timestamp
            query = f"SELECT * FROM {WET_EVENT_TABLE} LIMIT 1"

            # Execute the query
            cursor.execute(query)
            last_data_entry = cursor.fetchall()

            if last_data_entry:
                for row in last_data_entry:
                    print(row)
                last_data_entry = last_data_entry[0]
                
                last_entry = {"initial_time": last_data_entry[0],
                              "average_temperature": last_data_entry[1],
                              "number_of_updates": last_data_entry[2],
                              "initial_soil_moisture": last_data_entry[3],
                              "time_estimate": last_data_entry[4]}
                return last_entry

            else:
                print("No rows found")

        finally:
            # Close the cursor and connection
            cursor.close()
            connection.close()
        
    def create_wet_event(self, data):
        """
        Insert data into a MariaDB database table.

        Parameters:
        - data: A dictionary containing column names and their corresponding values.

        Example:
        data = {'column1': 'value1', 'column2': 'value2'}
        """
        
        # Create MySQL connection
        connection = mysql.connector.connect(**db_config)
    

        try:
            # Create a cursor object to interact with the database
            cursor = connection.cursor()

            # Construct the SQL query to insert data
            columns = ', '.join(data.keys())
            values = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO {WET_EVENT_TABLE} ({columns}) VALUES ({values})"

            # Execute the query
            cursor.execute(query, tuple(data.values()))

            # Commit the changes to the database
            connection.commit()

            print(f"{cursor.rowcount} row(s) inserted into the {WET_EVENT_TABLE} table.")

        finally:
            # Close the cursor and connection
            cursor.close()
            connection.close()

    def update_wet_event(self, update_data):
        """
        Update columns in a MariaDB database table.

        Parameters:
        - update_data: A dictionary containing column names and their corresponding values to update.
        Example:
        update_data = {'column1': 'new_value1', 'column2': 'new_value2'}
        update_columns('your_host', 'your_user', 'your_password', 'your_database', 'your_table', update_data, where_condition)
        """
        # Create MySQL connection
        connection = mysql.connector.connect(**db_config)
        try:
            # Create a cursor object to interact with the database
            cursor = connection.cursor()

            # Construct the SQL query to update columns
            set_clause = ', '.join([f"{column} = %s" for column in update_data.keys()])
            query = f"UPDATE {WET_EVENT_TABLE} SET {set_clause}"

            # Execute the query
            cursor.execute(query, list(update_data.values()))

            # Commit the changes to the database
            connection.commit()

            print(f"{cursor.rowcount} row(s) updated in the {WET_EVENT_TABLE} table.")

        finally:
            # Close the cursor and connection
            cursor.close()
            connection.close()   

    def reset_ongoing_wet_event(self):
        # Create MySQL connection
        connection = mysql.connector.connect(**db_config)
        try:
            # Create a cursor object to interact with the database
            cursor = connection.cursor()
            # Construct the SQL query to delete all data from the table
            query = f"DELETE FROM {WET_EVENT_TABLE}"
            # Execute the query
            cursor.execute(query)
            # Commit the changes to the database
            connection.commit()
            print(f"All data deleted from the {WET_EVENT_TABLE} table.")
        finally:
            # Close the cursor and connection
            cursor.close()
            connection.close()

    def save_event_to_history(self, wet_event_data):
        """
        Insert data into a MariaDB database table.

        Parameters:
        - data: A dictionary containing column names and their corresponding values.

        Example:
        data = {'initial_time': timestamp, 'average_temperature': double, 
                'initial_soil_moisture': double, 'time_to_dry': double hours}
        """
        # Create MySQL connection
        connection = mysql.connector.connect(**db_config)
        try:
            # Create a cursor object to interact with the database
            cursor = connection.cursor()

            # Construct the SQL query to insert data
            columns = ', '.join(wet_event_data.keys())
            values = ', '.join(['%s'] * len(wet_event_data))
            query = f"INSERT INTO {HISTORY_TABLE} ({columns}) VALUES ({values})"

            # Execute the query
            cursor.execute(query, tuple(wet_event_data.values()))

            # Commit the changes to the database
            connection.commit()

            print(f"{cursor.rowcount} row(s) inserted into the {HISTORY_TABLE} table.")

        finally:
            # Close the cursor and connection
            cursor.close()
            connection.close()

    def get_last_drying_time(self):
        # Connect to the database
        connection = mysql.connector.connect(**db_config)

        try:
            # Create a cursor object to interact with the database
            cursor = connection.cursor()

            # Example SELECT query to get the last 60,000 entries ordered by timestamp
            query = f"SELECT * FROM {HISTORY_TABLE} ORDER BY initial_time DESC LIMIT 1"

            # Execute the query
            cursor.execute(query)

            # Fetch the last 60,000 entries
            last_entry = cursor.fetchall()

            if last_entry:
                for row in last_entry:
                    print(row)
                last_entry = last_entry[0]
                last_entry = {"initial_time": last_entry[0],
                              "average_temperature": last_entry[1],
                              "initial_soil_moisture": last_entry[2],
                    "time_to_dry": last_entry[3]}
                return last_entry
            else:
                print("No rows found")

        finally:
            # Close the cursor and connection
            cursor.close()
            connection.close()