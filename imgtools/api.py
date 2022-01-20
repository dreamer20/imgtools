from flask import Blueprint, request, jsonify

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'gif', 'png'}
bp = Blueprint('api', __name__, url_prefix='/api')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def withFileCheck(f):

    def wrapper(*args, **kwargs):
        # check file presence
        # if file not in request send error
        # check file extentions
        # if file extention not allowed send error
        if 'image' not in request.files:
            return jsonify({'error': 'Файл отсутствует'}), 400
        imageFile = request.files['image']
        if imageFile.filename == '':
            return jsonify({'error': 'Изображение не выбрано'}), 400
        if imageFile and allowed_file(imageFile.filename):
            return f(*args, **kwargs)
        else:
            return jsonify({'error':'Расширение не поддерживается'}), 400
    return wrapper


@bp.route('/reflect', methods=['POST'])
@withFileCheck
def reflect():
    return 'Ok'
    # open image file with Pillow
    # make transformation
    # if transformation isn't successful send error
    # save image
    # send image to client
