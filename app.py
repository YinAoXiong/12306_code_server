# -*- coding: utf-8 -*-
import io
import base64
import flask
import numpy as np
from PIL import Image, ImageFile
from verify import pretreatment
import tflite_runtime.interpreter as tflite

app = flask.Flask(__name__)
# 模型的全局变量
textModel = None
imgModel = None
# 设置加载截断的图片，解决issue #10
ImageFile.LOAD_TRUNCATED_IMAGES = True


@app.before_first_request
def load_model():
    '''
    加载模型函数
    :return:
    '''
    global textModel
    global imgModel
    textModel = tflite.Interpreter(
        'text.model.tflite')
    textModel.allocate_tensors()
    imgModel = tflite.Interpreter(
        'image.model.tflite')
    imgModel.allocate_tensors()


def predict(model, input):
    input_details = model.get_input_details()
    output_details = model.get_output_details()
    model.set_tensor(input_details[0]['index'], np.float32(input))
    model.invoke()
    result = model.get_tensor(output_details[0]['index'])
    return result


def base64_to_image(base64_code):
    '''
    :param base64_code: base64编码的图片
    :return: bgr格式的图片
    '''
    # base64解码
    img_data = base64.b64decode(base64_code)
    # 读取图片
    img = np.asarray(Image.open(io.BytesIO(img_data)))
    # 转换为bgr格式
    img = img[..., ::-1]

    return img


def get_text(img, offset=0):
    '''
    得到图片中文字的部分
    :param img: 原始图像
    :param offset:
    :return: 文字部分的灰度图像
    '''
    text = pretreatment.get_text(img, offset)
    text = text[..., 0] * 0.114 + text[..., 1] * 0.587 + text[
        ..., 2] * 0.299
    text = text / 255.0
    h, w = text.shape
    text.shape = (1, h, w, 1)
    return text


def preprocess_input(x):
    x = x.astype('float32')
    # 我是用cv2来读取的图片，其已经是BGR格式了
    mean = [103.939, 116.779, 123.68]
    x -= mean
    return x


@app.route('/verify/base64/', methods=['POST'])
def predict_verify():
    verify_titles = ['打字机', '调色板', '跑步机', '毛线', '老虎', '安全帽', '沙包', '盘子', '本子', '药片', '双面胶', '龙舟', '红酒', '拖把', '卷尺',
                     '海苔', '红豆', '黑板', '热水袋', '烛台', '钟表', '路灯', '沙拉', '海报', '公交卡', '樱桃', '创可贴', '牌坊', '苍蝇拍', '高压锅',
                     '电线', '网球拍', '海鸥', '风铃', '订书机', '冰箱', '话梅', '排风机', '锅铲', '绿豆', '航母', '电子秤', '红枣', '金字塔', '鞭炮',
                     '菠萝', '开瓶器', '电饭煲', '仪表盘', '棉棒', '篮球', '狮子', '蚂蚁', '蜡烛', '茶盅', '印章', '茶几', '啤酒', '档案袋', '挂钟',
                     '刺绣',
                     '铃铛', '护腕', '手掌印', '锦旗', '文具盒', '辣椒酱', '耳塞', '中国结', '蜥蜴', '剪纸', '漏斗', '锣', '蒸笼', '珊瑚', '雨靴',
                     '薯条',
                     '蜜蜂', '日历', '口哨']
    if flask.request.method == 'POST':
        # 读取并预处理验证码
        img = flask.request.form['imageFile']
        img = base64_to_image(img)
        text = get_text(img)
        imgs = np.array(list(pretreatment._get_imgs(img)))
        imgs = preprocess_input(imgs)
        text_list = []
        label = predict(textModel, text)
        label = label.argmax()
        text = verify_titles[label]
        text_list.append(text)
        # 获取下一个词
        # 根据第一个词的长度来定位第二个词的位置
        if len(text) == 1:
            offset = 27
        elif len(text) == 2:
            offset = 47
        else:
            offset = 60
        text = get_text(img, offset=offset)
        if text.mean() < 0.95:
            label = predict(textModel, text)
            label = label.argmax()
            text = verify_titles[label]
            text_list.append(text)

        print(f"题目为{text_list}")
        labels = predict(imgModel, imgs)
        labels = labels.argmax(axis=1)
        results = []
        for pos, label in enumerate(labels):
            l = verify_titles[label]
            print(pos + 1, l)
            if l in text_list:
                results.append(str(pos + 1))
        if(len(results) != 0):
            return {'code': 0, 'massage': '识别成功', 'data': results}
        else:
            return {'code': 1, 'massage': '识别失败', 'data': results}


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
