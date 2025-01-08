from flask import Flask, jsonify, request
import requests, heapq, pytz
import datetime
from helper import helper_utils

app = Flask(__name__)

# API endpoint for getting concurrent calls
@app.route('/v1/get_concurrent_calls', methods=['GET'])
def get_concurrent_calls():
    user_key = request.args.get('userKey', '')
    if not user_key:
        return jsonify({'error': 'userKey is required'}), 400

    # Fetch records
    dataset_url = f"https://candidate.hubteam.com/candidateTest/v3/problem/dataset?userKey={user_key}"
    endpoint = f"https://candidate.hubteam.com/candidateTest/v3/problem/result?userKey={user_key}"
    response = requests.get(dataset_url)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch data from external API'}), 500

    call_records = response.json().get('callRecords', [])
    customer_call_data = {}

    # Process caall records for each customer call
    for call in call_records:
        customer_id = call['customerId']
        if customer_id not in customer_call_data:
            customer_call_data[customer_id] = {'call_dates': {}}

        call_dates = helper_utils.get_dates_between_timestamps(call['startTimestamp'], call['endTimestamp']-1)

        for call_date in call_dates:
            start_of_day = datetime.datetime.strptime(call_date, '%Y-%m-%d').replace(
                hour=0, minute=0, second=0, microsecond=0)
            start_of_day_unix = helper_utils.convert_date_to_unix_timestamp(start_of_day)

            if start_of_day.astimezone(pytz.UTC) < datetime.datetime.fromtimestamp(call['startTimestamp'] / 1000, pytz.UTC):
                start_of_day_unix = call['startTimestamp']

            if call_date not in customer_call_data[customer_id]['call_dates']:
                customer_call_data[customer_id]['call_dates'][call_date] = [[start_of_day_unix, call['endTimestamp'], call['callId']]]
            else:
                customer_call_data[customer_id]['call_dates'][call_date].append([start_of_day_unix, call['endTimestamp'], call['callId']])

    result_data = {'results': []}

    for customer_id in customer_call_data.keys():
        for call_date in customer_call_data[customer_id]['call_dates']:
            time_intervals = customer_call_data[customer_id]['call_dates'][call_date]
            time_intervals.sort(key=lambda x: x[0])

            max_concurrent_calls = 0
            concurrent_call_timestamps = {}
            end_time_heap = []
            active_call_ids = set()
            current_concurrent_calls = 0
            heapq.heapify(end_time_heap)

            for start_time, end_time, call_id in time_intervals:
                while end_time_heap and end_time_heap[0][0] <= start_time:
                    ended_time, ended_call_id = heapq.heappop(end_time_heap)
                    current_concurrent_calls -= 1
                    active_call_ids.remove(ended_call_id)

                current_concurrent_calls += 1
                active_call_ids.add(call_id)

                if end_time_heap:
                    if current_concurrent_calls not in concurrent_call_timestamps:
                        concurrent_call_timestamps[current_concurrent_calls] = [[active_call_ids.copy(), min(end_time_heap[0][0], start_time)]]
                    else:
                        concurrent_call_timestamps[current_concurrent_calls].append([active_call_ids.copy(), min(end_time_heap[0][0], start_time)])
                else:
                    if current_concurrent_calls not in concurrent_call_timestamps:
                        concurrent_call_timestamps[current_concurrent_calls] = [[active_call_ids.copy(), start_time]]
                    else:
                        concurrent_call_timestamps[current_concurrent_calls].append([active_call_ids.copy(), start_time])

                heapq.heappush(end_time_heap, (end_time, call_id))
                max_concurrent_calls = max(max_concurrent_calls, current_concurrent_calls)

            max_concurrent_call_data = concurrent_call_timestamps[max_concurrent_calls][0]
            response_body = {
                "customerId": customer_id,
                "date": call_date,
                "maxConcurrentCalls": max_concurrent_calls,
                "timestamp": max_concurrent_call_data[1],
                "callIds": list(max_concurrent_call_data[0])
            }
            result_data['results'].append(response_body)
    print(len(result_data['results']))
    response = requests.post(endpoint, json=result_data)
    print(response.text)
    return {'res':response.text}

if __name__ == '__main__':
    app.run(debug=True)
