import requests
from datetime import datetime, timezone
from collections import defaultdict
import json

def fetch_data(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code}")
    return response.json()['callRecords']

def timestamp_to_date(timestamp):
    return datetime.fromtimestamp(timestamp/1000, tz=timezone.utc).strftime('%Y-%m-%d')

def find_concurrent_calls(calls):
    results = []
    
    # Group calls by customer
    customer_calls = defaultdict(list)
    for call in calls:
        customer_calls[call['customerId']].append(call)
    
    for customer_id, customer_calls_list in customer_calls.items():
        # Track calls by date
        date_events = defaultdict(list)
        
        # Create events for start and end of each call
        for call in customer_calls_list:
            start_date = timestamp_to_date(call['startTimestamp'])
            end_date = timestamp_to_date(call['endTimestamp'])
            
            # Handle calls spanning multiple days
            current_date = datetime.fromtimestamp(call['startTimestamp']/1000, tz=timezone.utc)
            end_datetime = datetime.fromtimestamp(call['endTimestamp']/1000, tz=timezone.utc)
            
            while current_date.strftime('%Y-%m-%d') <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                date_events[date_str].append({
                    'timestamp': call['startTimestamp'] if date_str == start_date else int(current_date.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000),
                    'end_timestamp': call['endTimestamp'] if date_str == end_date else int((current_date.replace(hour=23, minute=59, second=59, microsecond=999999).timestamp() + 0.000001) * 1000),
                    'call_id': call['callId']
                })
                current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
                current_date = current_date.replace(day=current_date.day + 1)
        
        # Process each date
        for date, events in date_events.items():
            max_concurrent = 0
            max_timestamp = None
            max_call_ids = []
            
            # Check each event's timestamp
            for event in events:
                concurrent_calls = []
                timestamp = event['timestamp']
                
                # Find all overlapping calls at this timestamp
                for other_event in events:
                    if other_event['timestamp'] <= timestamp < other_event['end_timestamp']:
                        concurrent_calls.append(other_event['call_id'])
                
                if len(concurrent_calls) > max_concurrent:
                    max_concurrent = len(concurrent_calls)
                    max_timestamp = timestamp
                    max_call_ids = concurrent_calls
            
            results.append({
                'customerId': customer_id,
                'date': date,
                'maxConcurrentCalls': max_concurrent,
                'timestamp': max_timestamp,
                'callIds': max_call_ids
            })
    
    return results

def post_results(url, results):
    response = requests.post(url, json={'results': results})
    if response.status_code != 200:
        raise Exception(f"Failed to post results: {response.status_code} - {response.text}")
    print(response.status_code)
    print(response.text)
    return response

def main():
    user_key = ""
    base_url = ""
    
    # Fetch data
    calls = fetch_data(f"{base_url}/dataset?userKey={user_key}")
    
    # Process data
    results = find_concurrent_calls(calls)
    
    # Post results
    post_results(f"{base_url}/result?userKey={user_key}", results)

if __name__ == "__main__":
    main()
