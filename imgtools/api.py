from PIL import Image
from io import BytesIO
from flask import Blueprint, request, jsonify, send_file


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'gif', 'png'}
bp = Blueprint('api', __name__, url_prefix='/api')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def withFileCheck(f):

    def wrapper(*args, **kwargs):
        if 'image' not in request.files:
            return jsonify({'error': 'Файл отсутствует'}), 400
        imageFile = request.files['image']
        if imageFile.filename == '':
            return jsonify({'error': 'Изображение не выбрано'}), 400
        if imageFile and allowed_file(imageFile.filename):
            return f(*args, **kwargs)
        else:
            return jsonify({'error': 'Расширение не поддерживается'}), 400

    return wrapper


@bp.route('/reflect', methods=['POST'])
@withFileCheck
def reflect():
    direction = request.form['direction']
    img_file = request.files['image']
    bytes_io = BytesIO()

    with Image.open(img_file) as img:
        img_format = img.format

        if direction == 'horizontally':
            result_img = img.transpose(Image.FLIP_LEFT_RIGHT)
        elif direction == 'vertically':
            result_img = img.transpose(Image.FLIP_TOP_BOTTOM)
        result_img.save(bytes_io, format=img_format)

    bytes_io.seek(0)

    return send_file(bytes_io, mimetype=f'image/{img_format.lower()}')
