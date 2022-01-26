from PIL import Image, ImageFilter, ImageOps, ImageColor
from io import BytesIO
from flask import Blueprint, request, jsonify, send_file


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'gif', 'png'}
bp = Blueprint('api', __name__, url_prefix='/api')


@bp.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response


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

    wrapper.__name__ = f.__name__
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


@bp.route('/invert', methods=['POST'])
@withFileCheck
def invert():
    file = request.files['image']
    bytes_io = BytesIO()

    with Image.open(file) as img:
        resultImg = ImageOps.invert(img)
        resultImg.save(bytes_io, format=img.format)
    bytes_io.seek(0)

    return send_file(bytes_io, mimetype=f'image/{img.format.lower()}')


@bp.route('/solarize', methods=['POST'])
@withFileCheck
def solarize():
    file = request.files['image']
    threshold = int(request.form['threshold'])
    bytes_io = BytesIO()

    with Image.open(file) as img:
        resultImg = ImageOps.solarize(img, threshold)
        resultImg.save(bytes_io, format=img.format)
    bytes_io.seek(0)

    return send_file(bytes_io, mimetype=f'image/{img.format.lower()}')


@bp.route('/posterize', methods=['POST'])
@withFileCheck
def posterize():
    file = request.files['image']

    try:
        bits = int(request.form['bits'])
    except ValueError:
        return jsonify({'error': 'Некорректное значение.'}), 400

    if bits not in range(1, 9):
        return jsonify({'error': 'Некорректное значение.'}), 400

    bytes_io = BytesIO()

    with Image.open(file) as img:
        resultImg = ImageOps.posterize(img, bits)
        resultImg.save(bytes_io, format=img.format)
    bytes_io.seek(0)

    return send_file(bytes_io, mimetype=f'image/{img.format.lower()}')


@bp.route('/grayscale', methods=['POST'])
@withFileCheck
def grayscale():
    file = request.files['image']
    bytes_io = BytesIO()

    with Image.open(file) as img:
        resultImg = ImageOps.grayscale(img)
        resultImg.save(bytes_io, format=img.format)
    bytes_io.seek(0)

    return send_file(bytes_io, mimetype=f'image/{img.format.lower()}')


@bp.route('/border', methods=['POST'])
@withFileCheck
def border():
    file = request.files['image']
    fill = request.form['fill']

    try:
        fill = ImageColor.getrgb(fill)
        border_left = int(request.form['border_left'])
        border_top = int(request.form['border_top'])
        border_right = int(request.form['border_right'])
        border_bottom = int(request.form['border_bottom'])
    except ValueError:
        return jsonify({'error': 'Некорректное значение.'}), 400

    border = (border_left, border_top, border_right, border_bottom)
    bytes_io = BytesIO()

    with Image.open(file) as img:
        resultImg = ImageOps.expand(img, border, fill)
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


@bp.route('/equalize', methods=['POST'])
@withFileCheck
def equalize():
    file = request.files['image']
    bytes_io = BytesIO()

    with Image.open(file) as img:
        resultImg = ImageOps.equalize(img)
        resultImg.save(bytes_io, format=img.format)
    bytes_io.seek(0)

    return send_file(bytes_io, mimetype=f'image/{img.format.lower()}')


# @bp.route('/test', methods=['POST'])
# @withFileCheck
# def test():
#     file = request.files['image']
#     bytes_io = BytesIO()

#     with Image.open(file) as img:
#         resultImg = ImageOps.convert(img, deformer)  # Постеризация 
#         resultImg = img.convert('CMYK')
#         resultImg.save(bytes_io, format=img.format)
#     bytes_io.seek(0)

#     return send_file(bytes_io, mimetype=f'image/{img.format.lower()}')
