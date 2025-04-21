# 使用1M,2M代表万牌，1S,2S代表索牌，1P,2P代表筒牌
# 东西南北白发中分别为EWSNBFZ

from typing import List


class HandMajSet:
    def __init__(self,hidden_set: List[str], exposed_set: List[str], ):
        '''
        :param hidden_set: 暗牌（手牌）
        :param exposed_set: 明牌（吃碰杠）
        '''
        self.exposed_set = exposed_set
        self.hidden_set = hidden_set 