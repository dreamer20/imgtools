from PIL import Image, ImageFilter,  ImageEnhance, ImageChops, ImageOps
from io import BytesIO
from flask import Blueprint, request, jsonify, send_file

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
    wrapper.__name__ = f.__name__
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


@bp.route('/resize', methods=['POST'])
@withFileCheck
def resize():
    file = request.files['image']
    width = int(request.form['width'])
    height = int(request.form['height'])
    bytes_io = BytesIO()

    with Image.open(file) as img:
        resultImg = img.resize((width, height))
        resultImg.save(bytes_io, format=img.format)
    bytes_io.seek(0)

    return send_file(bytes_io, mimetype=f'image/{img.format.lower()}')


@bp.route('/rotate', methods=['POST'])
@withFileCheck
def rotate():
    file = request.files['image']
    degree = int(request.form['degree'])
    transpose_operations = {
        90: Image.ROTATE_90,
        180: Image.ROTATE_180,
        270: Image.ROTATE_270
    }
    bytes_io = BytesIO()

    with Image.open(file) as img:
        if (degree in transpose_operations):
            resultImg = img.transpose(transpose_operations[degree])
        else:
            resultImg = img.rotate(degree)
        resultImg.save(bytes_io, format=img.format)
    bytes_io.seek(0)

    return send_file(bytes_io, mimetype=f'image/{img.format.lower()}')


@bp.route('/filter', methods=['POST'])
@withFileCheck
def applyFilter():
    file = request.files['image']
    filterName = request.form['filterName']
    imageFilters = (
        'BLUR',
        'DETAIL'
    )
    bytes_io = BytesIO()

    with Image.open(file) as img:
        if (filterName in imageFilters):
            resultImg = img.filter(getattr(ImageFilter, filterName))
        else:
            return jsonify({'error': 'Операция не выполнима.'}), 400
        resultImg.save(bytes_io, format=img.format)
    bytes_io.seek(0)

    return send_file(bytes_io, mimetype=f'image/{img.format.lower()}')


@bp.route('/test', methods=['POST'])
@withFileCheck
def test():
    file = request.files['image']
    file2 = request.files['image2']
    bytes_io = BytesIO()

    with Image.open(file) as img:
        resultImg = ImageOps.invert(img)
        resultImg.save(bytes_io, format=img.format)
    bytes_io.seek(0)

    return send_file(bytes_io, mimetype=f'image/{img.format.lower()}')
