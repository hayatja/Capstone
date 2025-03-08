<?php
// Define the host and port
$host = '0.0.0.0'; // Listen on all available interfaces
$port = 8000;

// database credentials
$servername = "localhost";
$username = "ixtar";
$password = "capstone123";
$database = "AUTOBASE";

// Create a socket
$socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);

// Bind the socket to the address and port
socket_bind($socket, $host, $port);

// Start listening for incoming connections
socket_listen($socket);

echo "Server listening on $host:$port\n";

// Accept incoming connections
while (true) {

    $clientSocket = socket_accept($socket);
    // Read the request from the client
    $request = socket_read($clientSocket, 2048);
    // echo "Received request:\n$request\n";

    // Create sql connection
    $conn = new mysqli($servername, $username, $password, $database);
    // Check connection
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }


    if (str_contains($request, "GET")) {
        // if read request
        // Perform a query (for example, fetching data from a table)
        $query = "SELECT * FROM SENSOR_DATA ORDER BY timestamp DESC LIMIT 1";
        $result = $conn->query($query);
        
        unset($data);

        if ($result->num_rows > 0) {
            // Store data in an array
            while ($row = $result->fetch_assoc()) {
                $data[] = $row;
            }
        } else {
            $data['message'] = "No results found";
        }

        $query = "SELECT * FROM ONGOING_WET_EVENT";
        $result = $conn->query($query);
        
        // $wet_event = []
        unset($wet_event);

        
        if ($result->num_rows > 0) {
            // Store data in an array
            while ($row = $result->fetch_assoc()) {
                $wet_event[] = $row;
            }
        } 
        
        if (isset($wet_event)) {
            $data['time_estimate'] = $wet_event[0]['time_estimate'];
            // print_r($data);
            // print_r($wet_event);
        }

        // Encode the $data array into JSON format
        $jsonData = json_encode($data);

        // Set the appropriate content type and length for the JSON data
        $response = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " . strlen($jsonData) . "\r\n\r\n" . $jsonData;

        // Write the response to the client socket
        socket_write($clientSocket, $response);

    } elseif (str_contains($request, "POST") && str_contains($request, "temperature")) {

        $message = null;
        list($request, $message) = explode("\r\n\r\n", $request);
        // echo "this is message\n";
        

        if (isset($message) && $message !== null) {
            // echo $message;
        } else {
            continue;
            // echo "message is either not set or is null.";
        }

        $dataToInsert = json_decode($message, true);
        // echo "\nthis is data to insert\n";
        // print_r($dataToInsert);

        // Construct and execute the SQL query to insert data
        $sql = "INSERT INTO SENSOR_DATA (temperature, soil_moisture, rain_level) VALUES (?, ?, ?)";
        $stmt = $conn->prepare($sql);

        // Bind parameters and execute the query
        $stmt->bind_param("ssi", $dataToInsert['temperature'], $dataToInsert['soil_moisture'], $dataToInsert['rain_level']);
        $stmt->execute();

        if ($stmt->affected_rows > 0) {
            // Set the appropriate content type and length for the JSON data
            $response = "HTTP/1.1 200 OK\r\n";
            $response .= "Content-Type: text/plain\r\n"; // Set the appropriate content type
            $response .= "Content-Length: " . strlen("Data inserted successfully!") . "\r\n\r\n";
            // The actual response content
            $response .= "Data inserted successfully!";

            // Write the response to the client socket
            socket_write($clientSocket, $response);

        } else {
            // Handle errors here by sending an appropriate HTTP error response
            $errorResponse = "HTTP/1.1 500 Internal Server Error\r\n";
            $errorResponse .= "Content-Type: text/plain\r\n";
            $errorResponse .= "Content-Length: " . strlen("Error: " . $conn->error) . "\r\n\r\n";
            $errorResponse .= "Error: " . $conn->error;
            echo "Error: " . $conn->error;

            // Write the error response to the client socket
            socket_write($clientSocket, $errorResponse);
        }

        // Close the connection
        $stmt->close();
    }
    // Close the connection
    socket_close($clientSocket);
    // Close the connection
    $conn->close();

    // run python script to run backend database operations
    // Define the Python script
    $pythonScript = "main.py";
    // Build the command to run the Python script
    $command = "python3 $pythonScript";
    // Execute the command and capture the output
    $output = shell_exec($command);

    // Print the output
    echo "Output: $output";
}