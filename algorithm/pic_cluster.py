# for model to cluster majs and return maj_entitys
# just mock now

import json
from random import randint
from typing import List
from algorithm import basic_unit
from global_data.maj_entity import MajEntity, MajRect

import math
from typing import Tuple, List

import heapq

# 处理流程如下
# 第一步处理，调用yolo模型返回所有识别出的麻将牌的信息
# 第二步处理，调用聚类算法，返回聚类信息
# 第三步 待定 处理，调用旋转卡壳算法，返回聚类后rect的坐标信息

def pic_2_rect_info(uuid: str, pic: any, recall):
    maj_indexs = solve_maj_pic_index(uuid, pic)
    
    maj_rects = cluster_maj_entity(maj_indexs)

    # maj_rects = get_rect_index(maj_indexs)

    recall(maj_rects)



def solve_maj_pic_index(uuid: str, pic: any) -> List[MajEntity]:
    # Simulate processing time
    import time
    # time.sleep(2)  # Simulate some processing time

    # Create a mock result with dummy coordinates
    # result = [MajEntity('maj_type', 650, 1650, 2400, 300)]
    result = []
    with open('tests/mock_yolo.json') as f:
        data = f.read()
        data = json.loads(data)
        predictions = data['predictions']
        print(predictions[49], predictions[67])
        scale_x = 4000/2060
        scale_y = 2250/1230
        base_x = -60
        base_y = -10
        for prediction in predictions:
            x_min = base_x + prediction['x'] * scale_x
            y_min = base_y + prediction['y'] * scale_y
            x_max = x_min + prediction['width'] * scale_x
            y_max = y_min + prediction['height'] * scale_y
            maj_type = prediction['class']
            maj_entity = MajEntity(maj_type, x_min, y_min, x_max, y_max)
            result.append(maj_entity)

    return result

# 聚类算法
def cluster_maj_entity(maj_entities: List[MajEntity]) -> List[MajRect]:
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
    
    pai_width = 0.2

    while (len(edges) > 0 and edges[0].lenth() < 20):
        heapq.heappop(edges)        

    last_lenth = edges[0].lenth()
    union_find = basic_unit.UnionFind(len(maj_entities))
    while len(edges) > 0:
        print(len(edges))
        edge = heapq.heappop(edges)
        print(edge.lenth())
        if union_find.connected(edge.index[0], edge.index[1]):
            continue
        # 边倍率有待更改/改为可调参数
        if edge.lenth() > last_lenth * 6:
            break
        union_find.union(edge.index[0], edge.index[1])
    rects: dict[int, MajEntity] = {}
    for i in range(len(maj_entities)):
        root = union_find.find(i)
        if root not in rects:
            rects[root] = MajRect()
        rects[root].add_maj_entity(maj_entities[i])
    return list(rects.values())


def get_rect_index(maj_entities: List[MajEntity]) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
    if not maj_entities:
        return ()

    # 获取所有麻将牌的中心点
    points = [(entity.x_center, entity.y_center) for entity in maj_entities]

    # 计算凸包
    hull = basic_unit.convex_hull(points)

    # 使用旋转卡壳算法计算最小矩形
    min_area = float('inf')
    best_rect = None

    for i in range(len(hull)):
        p1 = hull[i]
        p2 = hull[(i + 1) % len(hull)]

        # 计算边的方向向量
        edge_vector = (p2[0] - p1[0], p2[1] - p1[1])
        edge_length = math.sqrt(edge_vector[0] ** 2 + edge_vector[1] ** 2)
        unit_vector = (edge_vector[0] / edge_length, edge_vector[1] / edge_length)

        # 计算垂直向量
        perp_vector = (-unit_vector[1], unit_vector[0])

        # 投影点到边和垂直方向
        projections = [(basic_unit.dot(point, unit_vector), basic_unit.dot(point, perp_vector)) for point in hull]

        # 找到投影的最小和最大值
        min_proj_x = min(projections, key=lambda x: x[0])[0]
        max_proj_x = max(projections, key=lambda x: x[0])[0]
        min_proj_y = min(projections, key=lambda x: x[1])[1]
        max_proj_y = max(projections, key=lambda x: x[1])[1]

        # 计算矩形面积
        width = max_proj_x - min_proj_x
        height = max_proj_y - min_proj_y
        area = width * height

        if area < min_area:
            min_area = area
            best_rect = (
                (min_proj_x * unit_vector[0] + min_proj_y * perp_vector[0],
                    min_proj_x * unit_vector[1] + min_proj_y * perp_vector[1]),
                (max_proj_x * unit_vector[0] + min_proj_y * perp_vector[0],
                    max_proj_x * unit_vector[1] + min_proj_y * perp_vector[1]),
                (max_proj_x * unit_vector[0] + max_proj_y * perp_vector[0],
                    max_proj_x * unit_vector[1] + max_proj_y * perp_vector[1]),
                (min_proj_x * unit_vector[0] + max_proj_y * perp_vector[0],
                    min_proj_x * unit_vector[1] + max_proj_y * perp_vector[1])
            )

    return best_rect

