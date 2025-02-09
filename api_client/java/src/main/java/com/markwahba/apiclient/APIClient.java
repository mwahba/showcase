package com.markwahba.apiclient;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.DeserializationFeature;

import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import java.util.Set;
import java.util.HashSet;
import java.util.Comparator;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.UncheckedIOException;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.stream.Collectors;
import java.nio.charset.StandardCharsets;

public class APIClient {

    private static final String GET_URL = "";
    private static final String POST_URL = "";
    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper()
        .registerModule(new JavaTimeModule())
        .configure(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS, true)
        .configure(DeserializationFeature.READ_DATE_TIMESTAMPS_AS_NANOSECONDS, false);

    public List<CallRecord> getCallRecords(final String url) throws IOException {
        final InputStream inputStream = makeGetRequest(url);

        try {  
            return OBJECT_MAPPER.readValue(inputStream, CallRecordsWrapper.class).callRecords();  
        }  
        catch (IOException exc) {  
            throw new UncheckedIOException(exc);
        }
    }

    public InputStream makeGetRequest(String url) throws IOException {
        URL obj = new URL(url);
        HttpURLConnection con = (HttpURLConnection) obj.openConnection();
        
        // Set up the request
        con.setRequestMethod("GET");
        
        // Read the response
        int responseCode = con.getResponseCode();
        if (responseCode != HttpURLConnection.HTTP_OK) {
            throw new IOException("GET request failed with code: " + responseCode);
        }
        
        return con.getInputStream();
    }

    private List<CallRecord> splitCallsByDay(CallRecord call) {
        List<CallRecord> splitCalls = new ArrayList<>();
        LocalDate startDate = Instant.ofEpochMilli(call.startTimestamp()).atZone(ZoneId.of("UTC")).toLocalDate();
        LocalDate endDate = Instant.ofEpochMilli(call.endTimestamp()).atZone(ZoneId.of("UTC")).toLocalDate();
        
        if (startDate.equals(endDate)) {
            splitCalls.add(call);
            return splitCalls;
        }
    
        // Current day processing
        LocalDate currentDate = startDate;
        while (!currentDate.isAfter(endDate)) {
            long dayStart;
            long dayEnd;
            
            if (currentDate.equals(startDate)) {
                dayStart = call.startTimestamp();
            } else {
                dayStart = currentDate.atStartOfDay(ZoneId.of("UTC"))
                    .toInstant()
                    .toEpochMilli();
            }
            
            if (currentDate.equals(endDate)) {
                dayEnd = call.endTimestamp();
            } else {
                dayEnd = currentDate.atStartOfDay(ZoneId.of("UTC"))
                    .plusDays(1)
                    .toInstant()
                    .toEpochMilli();
            }
            
            if (dayStart != dayEnd) {
                splitCalls.add(new CallRecord(
                    call.customerId(), 
                    call.callId(), 
                    dayStart, 
                    dayEnd
                ));
            }
            
            currentDate = currentDate.plusDays(1);
        }
    
        return splitCalls;
    }

    public List<ResultEntry> findMaxConcurrentCalls(List<CallRecord> calls) {
        Map<Integer, List<CallRecord>> customerCalls = calls.stream()
            .collect(Collectors.groupingBy(CallRecord::customerId));
        
        List<ResultEntry> results = new ArrayList<>();
        
        for (Map.Entry<Integer, List<CallRecord>> entry : customerCalls.entrySet()) {
            int customerId = entry.getKey();
            List<CallRecord> customerCallsList = entry.getValue();
            
            // Track calls by date
            Map<String, List<DayEvent>> dateEvents = new HashMap<>();
            
            // Create events for start and end of each call
            for (CallRecord call : customerCallsList) {
                List<CallRecord> splitCalls = splitCallsByDay(call);
                for (CallRecord splitCall : splitCalls) {
                    String date = Instant.ofEpochMilli(splitCall.startTimestamp())
                        .atZone(ZoneId.of("UTC"))
                        .toLocalDate()
                        .toString();
                    
                    dateEvents.computeIfAbsent(date, k -> new ArrayList<>())
                        .add(new DayEvent(
                            splitCall.startTimestamp(),
                            splitCall.endTimestamp(),
                            splitCall.callId()
                        ));
                }
            }
            
            // Process each date
            for (Map.Entry<String, List<DayEvent>> dateEntry : dateEvents.entrySet()) {
                String date = dateEntry.getKey();
                List<DayEvent> events = dateEntry.getValue();
                
                int maxConcurrent = 0;
                Long maxTimestamp = null;
                List<String> maxCallIds = new ArrayList<>();
                
                // Check each event's timestamp
                for (DayEvent event : events) {
                    List<String> concurrentCalls = new ArrayList<>();
                    long timestamp = event.timestamp();
                    
                    // Find all overlapping calls at this timestamp
                    for (DayEvent otherEvent : events) {
                        if (otherEvent.timestamp() <= timestamp && timestamp < otherEvent.endTimestamp()) {
                            concurrentCalls.add(otherEvent.callId());
                        }
                    }
                    
                    if (concurrentCalls.size() > maxConcurrent) {
                        maxConcurrent = concurrentCalls.size();
                        maxTimestamp = timestamp;
                        maxCallIds = new ArrayList<>(concurrentCalls);
                    }
                }
                
                results.add(new ResultEntry(
                    customerId,
                    date,
                    maxConcurrent,
                    maxTimestamp,
                    maxCallIds
                ));
            }
        }
        
        return results.stream()
            .sorted(Comparator.comparing(ResultEntry::customerId)
                            .thenComparing(ResultEntry::date))
            .collect(Collectors.toList());
    }
    
    record DayEvent(long timestamp, long endTimestamp, String callId) {}

    public String makePostRequest(final String url, final List<ResultEntry> results) throws IOException {
        final ResultEntryWrapper wrapper = new ResultEntryWrapper(results);
        
        final URL obj = new URL(url);
        final HttpURLConnection con = (HttpURLConnection) obj.openConnection();
        
        // Set up the request
        con.setRequestMethod("POST");
        con.setRequestProperty("Content-Type", "application/json");
        con.setDoOutput(true);

        try (OutputStream os = con.getOutputStream()) {
            String output = OBJECT_MAPPER.writeValueAsString(wrapper);
            os.write(output.getBytes(StandardCharsets.UTF_8));
            os.flush();
        }

        int responseCode = con.getResponseCode();

        try (BufferedReader br = new BufferedReader(
            new InputStreamReader(
                responseCode == HttpURLConnection.HTTP_BAD_REQUEST 
                    ? con.getErrorStream() 
                    : con.getInputStream()
            ))) {
            String response = br.lines().collect(Collectors.joining());

            if (responseCode != HttpURLConnection.HTTP_OK && 
                responseCode != HttpURLConnection.HTTP_BAD_REQUEST) {
                throw new IOException("POST request failed with code: " + responseCode);
            }
            
            return response;
        }
    }

    public record CallRecordsWrapper(List<CallRecord> callRecords) {}
    public record CallRecord (int customerId, String callId, long startTimestamp, long endTimestamp) {}
    public record ResultEntryWrapper(List<ResultEntry> results) {}
    public record ResultEntry (int customerId, String date, int maxConcurrentCalls, long timestamp, List<String> callIds) {}

    public static void main(String[] args) {
        APIClient client = new APIClient();
        try {
            final List<CallRecord> callRecords = client.getCallRecords(GET_URL);
            // System.out.println("Call Records: " + callRecords);
            // System.out.println("Length: " + callRecords.size());

            final List<ResultEntry> maxConcurrentCalls = client.findMaxConcurrentCalls(callRecords);
            // maxConcurrentCalls.forEach((entry) -> {
            //     System.out.println("Customer: " + entry.customerId() + ", Date: " + entry.date() + ", Max Concurrent Calls: " + entry.maxConcurrentCalls() + ", Timestamp: " + entry.timestamp() + ", Call IDs: " + entry.callIds());
            // });

            final ResultEntryWrapper wrapper = new ResultEntryWrapper(maxConcurrentCalls);
            // final String prettyJson = OBJECT_MAPPER
            //     .writerWithDefaultPrettyPrinter()
            //     .writeValueAsString(wrapper);
            // System.out.println("JSON Payload:\n" + prettyJson);

            final String result = client.makePostRequest(POST_URL, maxConcurrentCalls);
            System.out.println("Result: " + result);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}