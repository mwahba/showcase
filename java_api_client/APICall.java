import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;

public class APIClient {

    private static final String API_BASE_URL = "https://api.example.com";
    private ObjectMapper objectMapper = new ObjectMapper();

    public static void main(String[] args) {
        APIClient client = new APIClient();
        try {
            // Create a sample user object
            User user = new User("John Doe", "john.doe@example.com");
            
            // POST the user to the API
            String responseJson = client.createUser(user);
            System.out.println("POST Response: " + responseJson);

            // GET all users from the API
            String getUsersResponse = client.getUsers();
            System.out.println("GET Response: " + getUsersResponse);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public String createUser(User user) throws IOException {
        String endpoint = "/users";
        String requestBody = objectMapper.writeValueAsString(user);
        
        return makePostRequest(API_BASE_URL + endpoint, requestBody);
    }

    public String getUsers() throws IOException {
        String endpoint = "/users";
        return makeGetRequest(API_BASE_URL + endpoint);
    }

    private String makePostRequest(String url, String jsonBody) throws IOException {
        URL obj = new URL(url);
        HttpURLConnection con = (HttpURLConnection) obj.openConnection();
        
        // Set up the request
        con.setRequestMethod("POST");
        con.setRequestProperty("Content-Type", "application/json");
        con.setDoOutput(true);
        
        // Send the JSON body
        byte[] outputBytes = jsonBody.getBytes("UTF-8");
        con.getOutputStream().write(outputBytes);
        
        // Read the response
        int responseCode = con.getResponseCode();
        if (responseCode != HttpURLConnection.HTTP_CREATED) {
            throw new IOException("POST request failed with code: " + responseCode);
        }
        
        return readResponse(con.getInputStream());
    }

    private String makeGetRequest(String url) throws IOException {
        URL obj = new URL(url);
        HttpURLConnection con = (HttpURLConnection) obj.openConnection();
        
        // Set up the request
        con.setRequestMethod("GET");
        
        // Read the response
        int responseCode = con.getResponseCode();
        if (responseCode != HttpURLConnection.HTTP_OK) {
            throw new IOException("GET request failed with code: " + responseCode);
        }
        
        return readResponse(con.getInputStream());
    }

    private String readResponse(java.io.InputStream inputStream) throws IOException {
        StringBuilder response = new StringBuilder();
        byte[] buffer = new byte[1024];
        int bytesRead;
        
        while ((bytesRead = inputStream.read(buffer)) != -1) {
            response.append(new String(buffer, 0, bytesRead));
        }
        
        return response.toString();
    }

    // Example User class for JSON serialization/deserialization
    public static class User {
        private String name;
        private String email;
        
        public User(String name, String email) {
            this.name = name;
            this.email = email;
        }
        
        @Override
        public String toString() {
            return "User{" +
                   "name='" + name + '\'' +
                   ", email='" + email + '\'' +
                   '}';
        }
    }

    // Example Response wrapper class for JSON deserialization
    public static class ResponseWrapper {
        private User data;
        
        @Override
        public String toString() {
            return "ResponseWrapper{" +
                   "data=" + data +
                   '}';
        }
    }
}