import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import com.markwahba.apiclient.APIClient;
import java.util.List;
import com.markwahba.apiclient.APIClient.CallRecord;
import com.markwahba.apiclient.APIClient.ResultEntry;
import com.markwahba.apiclient.APIClient.ResultEntryWrapper;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.DeserializationFeature;

import java.util.Comparator;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;
import java.util.Set;
import java.util.HashSet;
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

public class APIClientTest {
    @Test
    void testFindMaxConcurrentCalls_SingleCallSingleCustomer() {
        List<CallRecord> calls = List.of(
            new CallRecord(1, "call1", 1000L, 2000L)
        );
        
        List<ResultEntry> results = new APIClient().findMaxConcurrentCalls(calls);
        
        assertEquals(1, results.size());
        ResultEntry entry = results.get(0);
        assertEquals(1, entry.customerId());
        assertEquals(1, entry.maxConcurrentCalls());
        assertEquals(1000L, entry.timestamp());
        assertEquals(List.of("call1"), entry.callIds());
    }

    @Test
    void testFindMaxConcurrentCalls_OverlappingCallsSingleCustomer() {
        List<CallRecord> calls = List.of(
            new CallRecord(1, "call1", 1000L, 3000L),
            new CallRecord(1, "call2", 2000L, 4000L)
        );
        
        List<ResultEntry> results = new APIClient().findMaxConcurrentCalls(calls);
        
        assertEquals(1, results.size());
        ResultEntry entry = results.get(0);
        assertEquals(1, entry.customerId());
        assertEquals(2, entry.maxConcurrentCalls());
        assertEquals(2000L, entry.timestamp());
        assertEquals(List.of("call1", "call2"), entry.callIds());
    }

    @Test
    void testFindMaxConcurrentCalls_BackToBackCalls() {
        List<CallRecord> calls = List.of(
            new CallRecord(1, "call1", 100L, 200L),
            new CallRecord(1, "call2", 200L, 300L)  // starts exactly when call1 ends
        );
        
        List<ResultEntry> results = new APIClient().findMaxConcurrentCalls(calls);
        
        assertEquals(1, results.size());
        ResultEntry entry = results.get(0);
        assertEquals(1, entry.customerId());
        assertEquals(1, entry.maxConcurrentCalls());  // should be 1 since calls don't overlap
        assertEquals(100L, entry.timestamp());
        assertEquals(List.of("call1"), entry.callIds());
    }

    @Test
    void testFindMaxConcurrentCalls_MultipleCustomers() {
        List<CallRecord> calls = List.of(
            new CallRecord(1, "call1", 1000L, 3000L),
            new CallRecord(1, "call2", 2000L, 4000L),
            new CallRecord(2, "call3", 1500L, 2500L),
            new CallRecord(2, "call4", 2000L, 3000L)
        );
        
        List<ResultEntry> results = new APIClient().findMaxConcurrentCalls(calls);
        
        assertEquals(2, results.size());
        results.sort(Comparator.comparing(ResultEntry::customerId));
        
        assertEquals(2, results.get(0).maxConcurrentCalls());
        assertEquals(2, results.get(1).maxConcurrentCalls());
    }

    @Test
    void testFindMaxConcurrentCalls_EmptyList() {
        List<CallRecord> calls = List.of();
        
        List<ResultEntry> results = new APIClient().findMaxConcurrentCalls(calls);
        
        assertTrue(results.isEmpty());
    }

    @Test
    void testFindMaxConcurrentCalls_DifferentDays() {
        // One day difference in milliseconds
        long DAY_MS = 24 * 60 * 60 * 1000;
        
        List<CallRecord> calls = List.of(
            new CallRecord(1, "call1", 1000L, 2000L),
            new CallRecord(1, "call2", DAY_MS + 1000L, DAY_MS + 2000L)
        );
        
        List<ResultEntry> results = new APIClient().findMaxConcurrentCalls(calls);
        
        assertEquals(2, results.size());
        results.forEach(entry -> assertEquals(1, entry.maxConcurrentCalls()));
    }

    @Test
    void testFindMaxConcurrentCalls_CallSpanningMultipleDays() {
        // Call spanning 1970-01-01 23:00 to 1970-01-02 01:00 UTC
        List<CallRecord> calls = List.of(
            new CallRecord(1, "call1", 82800000L, 90000000L)  // 23:00 to 01:00
        );
        
        List<ResultEntry> results = new APIClient().findMaxConcurrentCalls(calls);
        results.sort(Comparator.comparing(ResultEntry::date));
        
        assertEquals(2, results.size());
        
        // First day (1970-01-01)
        ResultEntry firstDay = results.get(0);
        assertEquals(1, firstDay.customerId());
        assertEquals(1, firstDay.maxConcurrentCalls());
        assertEquals(82800000L, firstDay.timestamp());
        assertEquals(List.of("call1"), firstDay.callIds());
        assertEquals("1970-01-01", firstDay.date());
        
        // Second day (1970-01-02)
        ResultEntry secondDay = results.get(1);
        assertEquals(1, secondDay.customerId());
        assertEquals(1, secondDay.maxConcurrentCalls());
        assertEquals(86400000L, secondDay.timestamp());
        assertEquals(List.of("call1"), secondDay.callIds());
        assertEquals("1970-01-02", secondDay.date());
    }

    @Test
    void testApiIntegration() throws IOException {
        APIClient client = new APIClient();
        String TEST_DATASET_URL = "https://candidate.hubteam.com/candidateTest/v3/problem/test-dataset?userKey=270591afb63b5bc35102d782fa56";
        String TEST_ANSWER_URL = "https://candidate.hubteam.com/candidateTest/v3/problem/test-dataset-answer?userKey=270591afb63b5bc35102d782fa56";
        String TEST_RESULT_URL = "https://candidate.hubteam.com/candidateTest/v3/problem/test-result?userKey=270591afb63b5bc35102d782fa56";
        final ObjectMapper OBJECT_MAPPER = new ObjectMapper()
            .registerModule(new JavaTimeModule())
            .configure(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS, true)
            .configure(DeserializationFeature.READ_DATE_TIMESTAMPS_AS_NANOSECONDS, false);

        // Get test dataset
        List<CallRecord> testCalls = client.getCallRecords(TEST_DATASET_URL);
        
        // Get expected answer
        InputStream answerStream = client.makeGetRequest(TEST_ANSWER_URL);
        ResultEntryWrapper expectedAnswer = OBJECT_MAPPER.readValue(
            answerStream, 
            ResultEntryWrapper.class
        );

        // Generate our answer
        List<ResultEntry> ourAnswer = client.findMaxConcurrentCalls(testCalls);

        // Compare our answer with expected
        assertEquals(
            expectedAnswer.results().size(), 
            ourAnswer.size(), 
            "Number of results should match"
        );

        // Sort both lists by customerId and date for comparison
        Comparator<ResultEntry> comparator = 
            Comparator.comparing(ResultEntry::customerId)
                    .thenComparing(ResultEntry::date);

        List<ResultEntry> sortedExpected = expectedAnswer.results()
            .stream()
            .sorted(comparator)
            .toList();

        List<ResultEntry> sortedOurs = ourAnswer
            .stream()
            .sorted(comparator)
            .toList();

        // Compare each result
        for (int i = 0; i < sortedExpected.size(); i++) {
            ResultEntry expected = sortedExpected.get(i);
            ResultEntry actual = sortedOurs.get(i);
            
            assertEquals(expected.customerId(), actual.customerId());
            assertEquals(expected.date(), actual.date());
            assertEquals(expected.maxConcurrentCalls(), actual.maxConcurrentCalls());
            assertEquals(expected.timestamp(), actual.timestamp());
            assertEquals(new HashSet<>(expected.callIds()), 
                    new HashSet<>(actual.callIds()));
        }

        // Verify with test endpoint
        String response = client.makePostRequest(TEST_RESULT_URL, ourAnswer);
        System.out.println("Response: " + response);
        assertTrue(response.contains("You provided the correct answer for the test dataset."),
                "Test endpoint should return success");
    }

    @Test
    void testFindMaxConcurrentCalls_CallEndsAtMidnight() {
        // One day in milliseconds
        long DAY_MS = 24 * 60 * 60 * 1000;
        
        List<CallRecord> calls = List.of(
            new CallRecord(1, "call1", DAY_MS - 1000, DAY_MS), // Ends exactly at midnight
            new CallRecord(1, "call2", DAY_MS, DAY_MS + 1000)  // Starts at midnight
        );
        
        List<ResultEntry> results = new APIClient().findMaxConcurrentCalls(calls);
        
        assertEquals(2, results.size());
        results.forEach(entry -> assertEquals(1, entry.maxConcurrentCalls()));
    }

    @Test
    void testFindMaxConcurrentCalls_MillisecondPrecision() {
        List<CallRecord> calls = List.of(
            new CallRecord(1, "call1", 1000L, 2000L),
            new CallRecord(1, "call2", 2000L, 3000L), // Starts exactly when call1 ends
            new CallRecord(1, "call3", 1999L, 3000L)  // Overlaps with call1 by 1ms
        );
        
        List<ResultEntry> results = new APIClient().findMaxConcurrentCalls(calls);
        
        assertEquals(1, results.size());
        ResultEntry entry = results.get(0);
        assertEquals(2, entry.maxConcurrentCalls());
        assertEquals(2000L, entry.timestamp());
        assertEquals(List.of("call2", "call3"), entry.callIds());
    }

    @Test
    void testFindMaxConcurrentCalls_MultiDaySpan() {
        // One day in milliseconds
        long DAY_MS = 24 * 60 * 60 * 1000;
        
        // Call starts at 23:00 Day 1, ends at 01:00 Day 3
        List<CallRecord> calls = List.of(
            new CallRecord(
                123, 
                "multiDayCall",
                DAY_MS - (1 * 60 * 60 * 1000),  // 23:00 Day 1
                (2 * DAY_MS) + (1 * 60 * 60 * 1000)  // 01:00 Day 3
            )
        );
        
        List<ResultEntry> results = new APIClient().findMaxConcurrentCalls(calls);
        
        // Sort results by date for consistent testing
        results.sort(Comparator.comparing(ResultEntry::date));
        
        // Should have one entry per day (3 days)
        assertEquals(3, results.size(), "Should have entry for each day");
        
        // Day 1
        ResultEntry day1 = results.get(0);
        assertEquals(123, day1.customerId());
        assertEquals(1, day1.maxConcurrentCalls());
        assertEquals(DAY_MS - (1 * 60 * 60 * 1000), day1.timestamp());
        assertEquals(List.of("multiDayCall"), day1.callIds());
        
        // Day 2
        ResultEntry day2 = results.get(1);
        assertEquals(123, day2.customerId());
        assertEquals(1, day2.maxConcurrentCalls());
        assertEquals(DAY_MS, day2.timestamp());
        assertEquals(List.of("multiDayCall"), day2.callIds());
        
        // Day 3
        ResultEntry day3 = results.get(2);
        assertEquals(123, day3.customerId());
        assertEquals(1, day3.maxConcurrentCalls());
        assertEquals(2 * DAY_MS, day3.timestamp());
        assertEquals(List.of("multiDayCall"), day3.callIds());
    }

    @Test
    void testFindMaxConcurrentCalls_MultipleMaxPeriods() {
        long HOUR_MS = 60 * 60 * 1000;
        long DAY_START = 24 * HOUR_MS; // Start at beginning of day
        
        List<CallRecord> calls = List.of(
            new CallRecord(123, "callA", 1000L, 3000L),
            new CallRecord(123, "callB", 2000L, 4000L),
            new CallRecord(123, "callC", 2500L, 4500L),
            
            new CallRecord(123, "callD", 4000L, 5000L),
            new CallRecord(123, "callE", 4500L, 5000L)
        );
        
        List<ResultEntry> results = new APIClient().findMaxConcurrentCalls(calls);
        
        assertEquals(1, results.size());
        ResultEntry entry = results.get(0);
        assertEquals(3, entry.maxConcurrentCalls());
        assertEquals(2500L, entry.timestamp());
        assertEquals(Set.of("callA", "callB", "callC"), new HashSet<>(entry.callIds()));
    }

    @Test
    void testFindMaxConcurrentCalls_ZeroLengthCall() {
        List<CallRecord> calls = List.of(
            new CallRecord(123, "call1", 1000L, 1000L), // Zero-length call
            new CallRecord(123, "call2", 1000L, 2000L),
            new CallRecord(123, "call3", 1500L, 2500L)
        );
        
        List<ResultEntry> results = new APIClient().findMaxConcurrentCalls(calls);
        
        assertEquals(1, results.size());
        ResultEntry entry = results.get(0);
        assertEquals(2, entry.maxConcurrentCalls());
        assertEquals(1500L, entry.timestamp());
        assertEquals(Set.of("call2", "call3"), new HashSet<>(entry.callIds()));
    }

    @Test
    void testFindMaxConcurrentCalls_ExactOverlapStarts() {
        List<CallRecord> calls = List.of(
            new CallRecord(123, "call1", 1000L, 2000L),
            new CallRecord(123, "call2", 1000L, 2000L),
            new CallRecord(123, "call3", 1000L, 2000L)
        );
        
        List<ResultEntry> results = new APIClient().findMaxConcurrentCalls(calls);
        assertEquals(1, results.size());
        ResultEntry entry = results.get(0);
        assertEquals(3, entry.maxConcurrentCalls());
        assertEquals(1000L, entry.timestamp());
        assertEquals(Set.of("call1", "call2", "call3"), new HashSet<>(entry.callIds()));
    }

    @Test
    void testFindMaxConcurrentCalls_DifferentMaxPeriods() {
        List<CallRecord> calls = List.of(
            // First max period
            new CallRecord(123, "call1", 1000L, 3000L),
            new CallRecord(123, "call2", 1000L, 3000L),
            // Different max period later
            new CallRecord(123, "call3", 4000L, 6000L),
            new CallRecord(123, "call4", 4000L, 6000L)
        );
        
        List<ResultEntry> results = new APIClient().findMaxConcurrentCalls(calls);
        assertEquals(1, results.size());
        ResultEntry entry = results.get(0);
        assertEquals(2, entry.maxConcurrentCalls());
        assertEquals(1000L, entry.timestamp());
        assertEquals(Set.of("call1", "call2"), new HashSet<>(entry.callIds()));
    }

    @Test
    void testFindMaxConcurrentCalls_CrossMidnightGroup() {
        long DAY_MS = 24 * 60 * 60 * 1000;
        
        List<CallRecord> calls = List.of(
            new CallRecord(123, "call1", DAY_MS - 1000, DAY_MS + 1000),
            new CallRecord(123, "call2", DAY_MS - 500, DAY_MS + 500),
            new CallRecord(123, "call3", DAY_MS - 250, DAY_MS + 250)
        );
        
        List<ResultEntry> results = new APIClient().findMaxConcurrentCalls(calls);
        results.sort(Comparator.comparing(ResultEntry::date));
        
        assertEquals(2, results.size());
        // First day
        assertEquals(3, results.get(0).maxConcurrentCalls());
        assertEquals(DAY_MS - 250, results.get(0).timestamp());
        assertEquals(Set.of("call1", "call2", "call3"), 
                    new HashSet<>(results.get(0).callIds()));
        // Second day
        assertEquals(3, results.get(1).maxConcurrentCalls());
        assertEquals(DAY_MS, results.get(1).timestamp());
        assertEquals(Set.of("call1", "call2", "call3"), 
                    new HashSet<>(results.get(1).callIds()));
    }
}