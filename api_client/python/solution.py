from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime, date
import requests
import json
from collections import defaultdict

@dataclass
class CallRecord:
    customerId: int
    callId: str
    startTimestamp: int
    endTimestamp: int

@dataclass
class TimelineEvent:
    time: int
    is_start: bool
    call_id: str
    
    def get_value(self) -> int:
        return 1 if self.is_start else -1

@dataclass
class ResultEntry:
    customerId: int
    date: str
    maxConcurrentCalls: int
    timestamp: int
    callIds: List[str]

def split_call_by_day(call: CallRecord) -> List[CallRecord]:
    splits = []
    DAY_MS = 24 * 60 * 60 * 1000
    
    start_date = datetime.utcfromtimestamp(call.startTimestamp / 1000).date()
    end_date = datetime.utcfromtimestamp(call.endTimestamp / 1000).date()
    
    # Handle midnight boundary
    if call.endTimestamp % DAY_MS == 0:
        end_date = datetime.utcfromtimestamp((call.endTimestamp - 1) / 1000).date()
    
    if start_date == end_date:
        splits.append(call)
        return splits
    
    # First day
    end_of_first_day = int(datetime(
        start_date.year, start_date.month, start_date.day, 23, 59, 59, 999999
    ).timestamp() * 1000)
    splits.append(CallRecord(
        call.customerId, call.callId,
        call.startTimestamp, end_of_first_day
    ))
    
    # Middle days
    current_date = start_date
    while current_date < end_date:
        current_date = date.fromordinal(current_date.toordinal() + 1)
        day_start = int(datetime(
            current_date.year, current_date.month, current_date.day
        ).timestamp() * 1000)
        day_end = int(datetime(
            current_date.year, current_date.month, current_date.day, 23, 59, 59, 999999
        ).timestamp() * 1000)
        
        if current_date < end_date:
            splits.append(CallRecord(
                call.customerId, call.callId,
                day_start, day_end
            ))
    
    # Last day
    start_of_last_day = int(datetime(
        end_date.year, end_date.month, end_date.day
    ).timestamp() * 1000)
    splits.append(CallRecord(
        call.customerId, call.callId,
        start_of_last_day, call.endTimestamp
    ))
    
    return splits

def find_max_concurrent_calls(calls: List[CallRecord]) -> List[ResultEntry]:
    results = []
    by_customer = defaultdict(list)
    
    # Split calls by day and group by customer
    for call in calls:
        if call.startTimestamp != call.endTimestamp:  # Skip zero-length calls
            for split_call in split_call_by_day(call):
                by_customer[split_call.customerId].append(split_call)
    
    # Process each customer's calls
    for customer_id, customer_calls in by_customer.items():
        by_date = defaultdict(list)
        
        # Group by date
        for call in customer_calls:
            call_date = datetime.utcfromtimestamp(call.startTimestamp / 1000).date()
            by_date[call_date].append(call)
        
        # Process each date
        for day_date, daily_calls in by_date.items():
            timeline = []
            
            # Create timeline events
            for call in daily_calls:
                timeline.append(TimelineEvent(call.startTimestamp, True, call.callId))
                timeline.append(TimelineEvent(call.endTimestamp, False, call.callId))
            
            timeline.sort(key=lambda x: x.time)
            
            current_calls = 0
            max_calls = 0
            max_timestamp = None
            current_call_ids = set()
            max_call_ids = []
            last_start = timeline[0].time
            
            # Process timeline events
            for event in timeline:
                if event.is_start:
                    current_call_ids.add(event.call_id)
                    last_start = event.time
                else:
                    current_call_ids.remove(event.call_id)
                
                current_calls += event.get_value()
                
                if current_calls >= max_calls:
                    if current_calls > max_calls or event.is_start:
                        max_calls = current_calls
                        max_timestamp = last_start
                        max_call_ids = list(current_call_ids)
            
            results.append(ResultEntry(
                customer_id,
                day_date.isoformat(),
                max_calls,
                max_timestamp,
                max_call_ids
            ))
    
    # Sort results
    results.sort(key=lambda x: (x.customerId, x.date))
    return results

def main():
    # Get data
    GET_URL = ""
    POST_URL = ""
    
    response = requests.get(GET_URL)
    data = response.json()
    
    # Convert to CallRecords
    calls = [CallRecord(**call) for call in data['callRecords']]
    
    # Process calls
    results = find_max_concurrent_calls(calls)
    
    # Prepare and send results
    payload = {
        'results': [vars(result) for result in results]
    }
    
    response = requests.post(POST_URL, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    main()