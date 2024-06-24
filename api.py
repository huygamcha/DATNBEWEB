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
        
    print('result', result)
    return jsonify(result)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)