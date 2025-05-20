from typing import List

maj_types = ['1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m',
             '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s',
             '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p',
             'e', 's', 'w', 'n',
             'b', 'f', 'z'
             'r5s', 'r5p', 'r5m']  # 作为统一标识符


class MajEntity:
    def __init__(self, maj_type, x_min, y_min, x_max, y_max):
        self.maj_type = maj_type
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        self.x_center = (x_min + x_max) / 2
        self.y_center = (y_min + y_max) / 2

    def get_rect_index(self):
        return self.x_min, self.y_min, self.x_max, self.y_max

    def set_fa_entity(self, fa_entity: 'MajEntity'):
        self.fa = fa_entity


# 被聚类后的麻将选框
class MajRect:
    def __init__(self):
        self.maj_entities: List[MajEntity] = []
        self.rect_x_max = None
        self.rect_x_min = None
        self.rect_y_max = None
        self.rect_y_min = None
        self.x_min_entity = None
        self.x_max_entity = None
        self.y_min_entity = None
        self.y_max_entity = None

    def add_maj_entity(self, maj_entity: MajEntity):
        self.maj_entities.append(maj_entity)
        self.update_rect(maj_entity)

    def update_rect(self, maj_entity: MajEntity):
        if self.rect_x_min is None or maj_entity.x_min < self.rect_x_min:
            self.rect_x_min = maj_entity.x_min
            self.x_min_entity = maj_entity
        if self.rect_x_max is None or maj_entity.x_max > self.rect_x_max:
            self.rect_x_max = maj_entity.x_max
            self.x_max_entity = maj_entity
        if self.rect_y_min is None or maj_entity.y_min < self.rect_y_min:
            self.rect_y_min = maj_entity.y_min
            self.y_min_entity = maj_entity
        if self.rect_y_max is None or maj_entity.y_max > self.rect_y_max:
            self.rect_y_max = maj_entity.y_max
            self.y_max_entity = maj_entity

    def get_rect_index(self):
        return self.rect_x_min, self.rect_y_min, self.rect_x_max - self.rect_x_min, self.rect_y_max - self.rect_y_min

    def get_maj_types(self):
        return [maj_entity.maj_type for maj_entity in self.maj_entities]
