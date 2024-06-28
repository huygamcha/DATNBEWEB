from flask import Flask, jsonify, request
from pymongo import MongoClient 
from flask_cors import CORS
import datetime


app = Flask(__name__)
CORS(app) 
CONNECTION_STRING = "mongodb+srv://huy6626:R72hkBXn4DcFSMe4@cluster0.ltvtchn.mongodb.net/"
client = MongoClient(CONNECTION_STRING)
db = client['result']
collection = db['human']

# Lấy toàn bộ số lượngn người ra, vào
@app.route('/countTotal', methods=['GET'])
def countGoingOut():
    countGoingOut = collection.count_documents({'action': 'go out'})
    countGoingIn = collection.count_documents({'action': 'go in'})
    return jsonify({'countGoingOut': countGoingOut, 'countGoingIn': countGoingIn})

# Lấy số lượng người ra vào theo khoảng thời gian tự chọn hôm nay
@app.route('/countTotalInTimeRange', methods=['GET'])
def countTotalInTimeRange():
    start_time = request.args.get('start')
    end_time = request.args.get('end')
    print('««««« start_time »»»»»', start_time)

    if not start_time or not end_time:
        return jsonify({'message': 'Yêu cầu phải đi kèm với tham số start và end'}), 400

    try:
        # Chuyển đổi chuỗi thời gian thành đối tượng datetime
        start_time = datetime.datetime.fromisoformat(start_time)
        end_time = datetime.datetime.fromisoformat(end_time)
    except ValueError:
        return jsonify({'message': 'Định dạng thời gian không hợp lệ. Định dạng hợp lệ: YYYY-MM-DDTHH:MM:SS'}), 400

    countGoingOut = collection.count_documents({'action': 'go out', 'time': {'$gte': start_time, '$lte': end_time}})
    countGoingIn = collection.count_documents({'action': 'go in', 'time': {'$gte': start_time, '$lte': end_time}})
    
    return jsonify({'countGoingOut': countGoingOut, 'countGoingIn': countGoingIn})

# Lấy số lượngn người ra, vào theo ngày tự chọn
@app.route('/countByPickerDate', methods=['GET'])
def countByPickerDate():
    start_time = request.args.get('start')
    end_time = request.args.get('end')
    print('««««« start_time »»»»»', start_time, end_time)

    if not start_time or not end_time:
        return jsonify({'message': 'Yêu cầu phải đi kèm với tham số start và end'}), 400

    try:
        # Chuyển đổi chuỗi thời gian thành đối tượng datetime
        start_time = datetime.datetime.fromisoformat(start_time)
        end_time = datetime.datetime.fromisoformat(end_time)
    except ValueError:
        return jsonify({'message': 'Định dạng thời gian không hợp lệ. Định dạng hợp lệ: YYYY-MM-DDTHH:MM:SS'}), 400

    print(start_time, end_time)
    countGoingOut = collection.count_documents({'action': 'go out', 'time': {'$gte': start_time, '$lte': end_time}})
    countGoingIn = collection.count_documents({'action': 'go in', 'time': {'$gte': start_time, '$lte': end_time}})
    
    return jsonify({'countGoingOut': countGoingOut, 'countGoingIn': countGoingIn})

@app.route('/countSevenAgo', methods=['GET'])
def countSevenAgo():
    start_time = request.args.get('start')
    select_day = request.args.get('day')

    if not start_time:
        return jsonify({'message': 'Yêu cầu phải đi kèm với tham số start'}), 400

    try:
        # Chuyển đổi chuỗi thời gian thành đối tượng datetime
        start_time = datetime.datetime.fromisoformat(start_time)
    except ValueError:
        return jsonify({'message': 'Định dạng thời gian không hợp lệ. Định dạng hợp lệ: YYYY-MM-DDTHH:MM:SS'}), 400

    # Tính end_time là 6 ngày sau start_time
    end_time = start_time - datetime.timedelta(days=int(select_day))

    # Khởi tạo biến để lưu kết quả
    result = []

    # Vòng lặp qua các ngày
    current_day = end_time
    while current_day <= start_time:
        # Tính start_of_day và end_of_day cho current_day
        start_of_day = current_day.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = current_day.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Đếm số lượng tài liệu cho ngày hiện tại
        countGoingOut = collection.count_documents({
            'action': 'go out',
            'time': {'$gte': start_of_day, '$lte': end_of_day}
        })
        countGoingIn = collection.count_documents({
            'action': 'go in',
            'time': {'$gte': start_of_day, '$lte': end_of_day}
        })

        # Thêm kết quả vào danh sách
        result.append({
            'date': start_of_day.date().isoformat(),  # Chỉ lấy phần ngày
            'countGoingOut': countGoingOut,
            'countGoingIn': countGoingIn
        })

        # Chuyển sang ngày tiếp theo
        current_day += datetime.timedelta(days=1)
        
    return jsonify(result)

@app.route('/countForTime', methods=['GET'])
def countForTime():
    start_time_str = request.args.get('start')
    select_day = request.args.get('day')

    if not start_time_str:
        return jsonify({'message': 'Yêu cầu phải đi kèm với tham số start'}), 400

    try:
        # Chuyển đổi chuỗi thời gian thành đối tượng datetime
        start_time = datetime.datetime.fromisoformat(start_time_str)
    except ValueError:
        return jsonify({'message': 'Định dạng thời gian không hợp lệ. Định dạng hợp lệ: YYYY-MM-DDTHH:MM:SS'}), 400

    try:
        # Chuyển select_day thành số nguyên
        select_day = int(select_day)
    except ValueError:
        return jsonify({'message': 'Ngày lựa chọn không hợp lệ. Phải là một số nguyên dương.'}), 400

    # Tính end_time là 'select_day' ngày trước start_time
    end_time = start_time - datetime.timedelta(days=select_day)

    # Khởi tạo biến để lưu kết quả
    hourly_counts = []

    # Vòng lặp qua các ngày trong khoảng thời gian từ end_time đến start_time
    current_day = end_time
    print(current_day, start_time)
    while current_day <= start_time:
        # Lặp qua mỗi giờ trong ngày
        for hour in range(24):
            # Tính start_of_hour và end_of_hour cho mỗi giờ
            start_of_hour = current_day.replace(hour=hour, minute=0, second=0, microsecond=0)
            end_of_hour = current_day.replace(hour=hour, minute=59, second=59, microsecond=999999)

            # Đếm số lượng tài liệu cho giờ hiện tại
            countGoingOut = collection.count_documents({
                'action': 'go out',
                'time': {'$gte': start_of_hour, '$lte': end_of_hour}
            })
            countGoingIn = collection.count_documents({
                'action': 'go in',
                'time': {'$gte': start_of_hour, '$lte': end_of_hour}
            })

            # Tạo cặp khoảng thời gian và dữ liệu goingIn, goingOut
            time_range = f"{hour:02}:00-{(hour+1) % 24:02}:00"
            hour_data = {
                'goingIn': countGoingIn,
                'goingOut': countGoingOut
            }

            # Thêm vào danh sách kết quả dưới dạng mong muốn
            hourly_counts.append([[time_range], [hour_data]])

        # Chuyển sang ngày tiếp theo
        current_day += datetime.timedelta(days=1)
        
    print({"hourly_counts": hourly_counts})
    # Trả về định dạng cuối cùng cho hourly_counts
    return jsonify({"hourly_counts": hourly_counts})
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)

