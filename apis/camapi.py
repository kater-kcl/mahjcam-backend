from flask import Blueprint, request, jsonify
from algorithm.maj_solve import solve_maj_pic_index


from global_data.global_data import GlobalData
from global_data.response_temple import make_response_template
import tempfile
import threading
import uuid

blueprint = Blueprint('camapi', __name__)

@blueprint.route('/upload', methods=['POST'])
def upload():  
    # print(request.files)
    if 'picture' not in request.files:
        return 'No file part'
    file = request.files['picture']
    if file.filename == '':
        return 'No selected file'
    

    fid = str(uuid.uuid4())
    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False, dir='./Temp/pics') as temp_file:
        file.save(temp_file.name)
        solve_maj_pic_index(fid, temp_file)
        
    content = {'uuid': fid}

    response = make_response_template('success', '000000', content)

    return response, 200

@blueprint.route('/result', methods=['GET'])
def get_result():
    # 获取body中的uuid
    uuid = request.args.get('uuid')


    scan_cluster = GlobalData.get_scan_cluster(uuid)

    if scan_cluster is None:
        return 'This is the result of the camera'

    if not scan_cluster.is_finished():
        response = make_response_template('The result is not ready', '020001', {})
        return response, 200

    results = scan_cluster.get_result()

    if results is None:
        return 'The result is None'
    
    # result = {
    #     'rect_index': [],
    # }
    result = {
        'rects': [],
    }
    for maj_rect in results:
        rect_index = maj_rect.get_rect_index()
        rect_info = {
            'rect_index': rect_index,
            'maj_types': maj_rect.get_maj_types(),
        }
        result['rects'].append(rect_info)

    response = make_response_template('success', '000000', result)

    return response, 200
