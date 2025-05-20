# for model to cluster majs and return maj_entitys
# just mock now

import json
from src.algorithm import basic_unit
from src.global_data.maj_entity import MajEntity, MajRect
import src.algorithm.yolo_model as yolo_model

import math
from typing import List

import heapq


# 处理流程如下
# 第一步处理，调用yolo模型返回所有识别出的麻将牌的信息
# 第二步处理，调用聚类算法，返回聚类信息
# 第三步 待定 处理，调用旋转卡壳算法，返回聚类后rect的坐标信息

def pic_2_rect_info(uuid: str, pic: any, recall):
    maj_indexs = solve_maj_pic_index(uuid, pic)

    maj_rects = cluster_maj_entity(maj_indexs)

    recall(maj_rects)


def solve_maj_pic_index(uuid: str, pic: any) -> List[MajEntity]:
    result = []
    # with open('tests/mock_yolo3.json') as f:
    #     data = f.read()
    #     data = json.loads(data)
    #     predictions = data['predictions']
    #     scale_x = 4000 / 2060
    #     scale_y = 2250 / 1230
    #     base_x = -60
    #     base_y = -10
    data = yolo_model.detect_and_format(pic.name)
    predictions = data['predictions']
    for prediction in predictions:
        # x_min = base_x + prediction['x'] * scale_x
        # y_min = base_y + prediction['y'] * scale_y
        # x_max = x_min + prediction['width'] * scale_x
        # y_max = y_min + prediction['height'] * scale_y
        x_min = prediction['x']
        y_min = prediction['y']
        x_max = x_min + prediction['width']
        y_max = y_min + prediction['height']
        maj_type = prediction['class']
        maj_entity = MajEntity(maj_type, x_min, y_min, x_max, y_max)
        result.append(maj_entity)

    return result


# 聚类算法
def cluster_maj_entity(maj_entities: List[MajEntity]) -> List[MajRect]:
    if maj_entities is None or len(maj_entities) == 0:
        return []
    edges = []

    class PointsEdge:
        def __init__(self, u: MajEntity, v: MajEntity, index_u: int = 0, index_v: int = 0):
            self.index = (index_u, index_v)
            self.u = u
            self.v = v

        def lenth(self):
            return math.sqrt((self.u.x_center - self.v.x_center) ** 2 + (self.u.y_center - self.v.y_center) ** 2)

        def __lt__(self, other):
            return self.lenth() < other.lenth()

    for i in range(len(maj_entities)):
        for j in range(i + 1, len(maj_entities)):
            edge = PointsEdge(maj_entities[i], maj_entities[j], i, j)
            heapq.heappush(edges, edge)

    while len(edges) > 0 and edges[0].lenth() < 100:
        heapq.heappop(edges)
    if len(edges) == 0:
        return []
    last_lenth = edges[0].lenth()
    union_find = basic_unit.UnionFind(len(maj_entities))
    while len(edges) > 0:
        edge = heapq.heappop(edges)
        if union_find.connected(edge.index[0], edge.index[1]):
            continue
        # 边倍率有待更改/改为可调参数
        if edge.lenth() > last_lenth * 2:
            break
        union_find.union(edge.index[0], edge.index[1])
    rects: dict[int, MajRect] = {}
    for i in range(len(maj_entities)):
        root = union_find.find(i)
        if root not in rects:
            rects[root] = MajRect()
        rects[root].add_maj_entity(maj_entities[i])
    return list(rects.values())

