from ultralytics import YOLO
from PIL import Image

# 加载模型和图像
model = YOLO("src/algorithm/model/best(3).pt")

kind_name = {0: '1S', 1: '2S', 2: '3S', 3: '4S', 4: '5S', 5: '6S', 6: '7S',
       7: '8S', 8: '9S', 9: '1M', 10: '2M', 11: '3M', 12: '4M',
       13: '5M', 14: '6M', 15: '7M', 16: '8M', 17: '9M',
       18: '1P', 19: '2P', 20: '3P', 21: '4P', 22: '5P', 23: '6P',
       24: '7P', 25: '8P', 26: '9P', 27: 'E', 28: 'F', 29: 'N', 30: 'Z', 31: 'S',
       32: 'W', 33: 'B'}


def detect_and_format(pic_path: str):
    image = Image.open(pic_path)
    # 执行预测
    results = model.predict(source=image, save=False)

    # 构建目标数据结构
    output = {"predictions": []}
    for result in results:
        orig_h, orig_w = result.orig_shape  # 原始图像高、宽
        input_h, input_w = result.boxes.orig_shape  # 预处理后的输入尺寸
        ratio = min(input_h / orig_h, input_w / orig_w)  # 缩放比例
        pad_x = (input_w - orig_w * ratio) / 2  # 水平方向的Padding
        pad_y = (input_h - orig_h * ratio) / 2  # 垂直方向的Padding
        if result.boxes is not None:
            for box, cls, conf in zip(result.boxes.xyxy, result.boxes.cls, result.boxes.conf):
                # 转换坐标格式
                x_min, y_min, x_max, y_max = box.cpu().numpy()
                x_min = (x_min - pad_x) / ratio
                y_min = (y_min - pad_y) / ratio
                x_max = (x_max - pad_x) / ratio
                y_max = (y_max - pad_y) / ratio
                # 计算中心点坐标和宽高
                detection = {
                    "x": float(x_min),  # 中心X坐标
                    "y": float(y_min),  # 中心Y坐标
                    "width": float(x_max - x_min),  # 检测框宽度
                    "height": float(y_max - y_min),  # 检测框高度
                    "confidence": float(conf),  # 置信度
                    "class": kind_name[int(cls)]  # 类别名称
                }
                if detection["confidence"] > 0.2:
                    output["predictions"].append(detection)
    return output
