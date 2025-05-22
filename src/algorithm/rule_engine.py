# 使用1M,2M代表万牌，1S,2S代表索牌，1P,2P代表筒牌
# R5M,R5S,R5P代表红宝牌
# 东西南北白发中分别为EWSNBFZ
# TODO: 全局修改len(cpg_list)改为修改支持暗杠的情况
from typing import List, Dict, Optional
from pydantic import BaseModel


class FormData(BaseModel):
    hand_tiles: List[str] = []  # 手牌
    outer_tiles: List[List[str]] = []  # 吃碰杠
    game_type: str = ""  # 三麻/四麻
    north_pulls: int = 0  # 拔北次数
    current_round: str = ""  # 场风
    self_round: str = ""  # 自风
    is_dealer: bool = False  # 是否庄家
    is_self_draw: bool = False  # 是否自摸
    is_riichi: bool = False  # 是否立直
    is_double_riichi: bool = False  # 是否两立直
    is_first_turn: bool = False  # 是否一发
    is_on_kang: bool = False  # 是否岭上
    is_catch_kang: bool = False  # 是否抢杠
    ready_indicators: List[str] = []  # 听牌指示牌
    dora_indicators: List[str] = []  # 宝牌指示牌
    ura_dora_indicators: List[str] = []  # 里宝指示牌
    is_river_or_sea: bool = False  # 是否河底/海底
    is_first_turn_win: bool = False  # 天和/地和
    concealed_kangs: int = 0  # 暗杠数量


# 役表
yi_list = {
    # 1番役
    "riichi": ("立直", 1),
    "ippatsu": ("一发", 1),
    "menzen_tsumo": ("门前清自摸和", 1),
    "tanyao": ("断幺九", 1),
    "pinfu": ("平和", 1),
    "iipeko": ("一杯口", 1),
    "yakuhai_haku": ("役牌 白", 1),
    "yakuhai_hatsu": ("役牌 发", 1),
    "yakuhai_chun": ("役牌 中", 1),
    "yakuhai_wind_round": ("役牌 场风", 1),
    "yakuhai_wind_seat": ("役牌 自风", 1),
    "haitei": ("海底摸月/河底捞鱼", 1),
    "rinshan": ("岭上开花", 1),
    "chankan": ("抢杠", 1),
    "dora": ("宝牌", 1),
    "ura_dora": ("里宝牌", 1),
    "red_dora": ("赤宝牌", 1),

    # 2番役
    "sanshoku": ("三色同顺", 2),
    "ittsu": ("一气通贯", 2),
    "chanta": ("混全带幺九", 2),
    "sankantsu": ("三杠子", 2),
    "toitoi": ("对对和", 2),
    "sananko": ("三暗刻", 2),
    "shosangen": ("小三元", 2),
    "double_riichi": ("双立直", 2),
    "qiedui": ("七对子", 2),

    # 3番役
    "honitsu": ("混一色", 3),
    "junchan": ("纯全带幺九", 3),
    "ryanpeikou": ("两杯口", 3),

    # 6番役
    "chinitsu": ("清一色", 6),
}

# 以下役种副露-1番
men_tsu_full = ['ittsu', 'chanta', 'sanshoku', 'junchan', 'honitsu', 'chinitsu']

yi_full_list = {
    # 役满
    "suanko": ("四暗刻", 1),
    "suankotanki": ("四暗刻单骑", 2),
    "daisangen": ("大三元", 1),
    "tsuiso": ("字一色", 1),
    "shosushi": ("小四喜", 1),
    "daisushi": ("大四喜", 2),
    "ryuiso": ("绿一色", 1),
    "chinroto": ("清老头", 1),
    "sukantsu": ("四杠子", 1),
    "chuuren": ("九莲宝灯", 1),
    "kokushi": ("国士无双", 1),
    "tenho": ("天和", 1),
    "chiho": ("地和", 1),
}


def dora_check(tilename):
    # 字牌
    if len(tilename) == 1:
        tile_li1 = ['E', 'S', 'W', 'N']
        tile_li2 = ['B', 'F', 'Z']
        if tilename in tile_li1:
            return tile_li1[(tile_li1.index(tilename) + 1) % len(tile_li1)]
        elif tilename in tile_li2:
            return tile_li2[(tile_li2.index(tilename) + 1) % len(tile_li2)]
    else:
        return str(int(tilename[0]) % 9 + 1) + tilename[1]


def calculate_points(fu, han, is_dealer, is_yiman=False):
    if is_yiman:
        base = 16000 * han
        if is_dealer:
            base *= 2
        else:
            base *= 3
        return base

    if han < 1:
        return 0  # 至少需要1番才能和牌

    # 计算基本点并进位到百位
    base = fu * (2 ** (2 + han))
    base = ((base + 99) // 100) * 100

    # 处理满贯及以上规则
    if han >= 5 or (han == 4 and base >= 2000):
        if han >= 13:
            base = 8000
        elif han >= 11:
            base = 6000
        elif han >= 8:
            base = 4000
        elif han >= 6:
            base = 3000
        else:
            base = 2000  # 5番或4番切上满贯

    # 计算最终点数
    if is_dealer:
        return base * 6  # 庄家荣和支付6倍
    else:
        return base * 4  # 闲家荣和支付4倍


def dfs_split(maj_count: Dict[str, int], ans: List, res_stack=None):
    """
    深度优先搜索拆分
    :return:
    """
    if res_stack is None:
        res_stack = []
    rest_list = [maj_type for maj_type in maj_count.keys() if maj_count[maj_type] != 0]
    if len(rest_list) == 0:
        # 结算牌谱
        ans.append(res_stack.copy())
        return
    now_maj = rest_list[0]
    now_count = maj_count[now_maj]
    if now_count >= 3:
        # 刻子
        maj_count[now_maj] -= 3
        dfs_split(maj_count, ans, res_stack + [[now_maj] * 3])
        maj_count[now_maj] += 3
    if len(now_maj) == 1:
        return
    maj_num = int(now_maj[0])
    maj_type = now_maj[1]
    shun_list = [f'{maj_num - 2}{maj_type}', f'{maj_num - 1}{maj_type}',
                 f'{maj_num}{maj_type}', f'{maj_num + 1}{maj_type}',
                 f'{maj_num + 2}{maj_type}']
    for i in range(3):
        if shun_list[i] not in maj_count:
            continue
        if shun_list[i + 1] not in maj_count:
            continue
        if shun_list[i + 2] not in maj_count:
            continue
        if maj_count[shun_list[i]] > 0 and maj_count[shun_list[i + 1]] > 0 and maj_count[shun_list[i + 2]] > 0:
            # 顺子
            maj_count[shun_list[i]] -= 1
            maj_count[shun_list[i + 1]] -= 1
            maj_count[shun_list[i + 2]] -= 1
            dfs_split(maj_count, ans, res_stack + [[shun_list[i], shun_list[i + 1], shun_list[i + 2]]])
            maj_count[shun_list[i]] += 1
            maj_count[shun_list[i + 1]] += 1
            maj_count[shun_list[i + 2]] += 1


# 检验牌型是否和牌
def check_pai(hand, cpg_list):
    if len(hand) == 1 and len(hand[0]) == 14:
        return True
    all_list = hand + cpg_list
    zu_count = 0
    que_head = False
    for piles in all_list:
        if len(piles) == 2:
            que_head = True
        if len(piles) == 3 or len(piles) == 4:
            zu_count += 1
    if zu_count == 4 and que_head:
        return True
    return False


all_majs = [f"{i}{t}" for t in ['M', 'P', 'S'] for i in range(1, 10)] + \
           ['E', 'W', 'S', 'N', 'B', 'F', 'Z']


class HandMajSet:
    def __init__(self, maj_data: FormData = None):
        """
        :param maj_data: 手牌数据
        """
        if maj_data is None:
            self.maj_data = FormData()
        else:
            self.maj_data = maj_data
        self.hidden_set = self.maj_data.hand_tiles
        # self.end_maj = [self.maj_data.ready_indicators[0], self.hidden_set[-1]][len(self.maj_data.ready_indicators) == 0]
        if len(self.maj_data.ready_indicators) != 0:
            self.end_maj = self.maj_data.ready_indicators[0]
        else:
            self.end_maj = self.hidden_set[-1]
        self.hidden_count = {}
        self.rcount = {
            'R5P': 0,
            'R5S': 0,
            'R5M': 0,
        }
        self.hand_list = []
        self.cpg_list = self.maj_data.outer_tiles
        for maj in self.hidden_set:
            if maj.startswith('R'):
                self.rcount[maj] += 1
                maj = maj[1:]
            if maj not in self.hidden_count:
                self.hidden_count[maj] = 0
            self.hidden_count[maj] += 1
        self.yi_infos = []

        # 特殊役种记录
        self.is_qidui = False
        self.is_guoshi = False

        self.tin_set = []

        self.split_init()

    def check_tin(self):
        # 听牌检测
        tin_set = []
        for tile in all_majs:
            # 预处理手牌
            temp_hand = self.hidden_set[:-1] + [tile]
            temp_form_data = FormData(hand_tiles=temp_hand)
            temp_hand_maj_set = HandMajSet(temp_form_data)
            if temp_hand_maj_set.check_valid():
                tin_set.append(tile)
                print(f"听牌: {tile}")
        return list(set(tin_set))

    def split_init(self):
        """
        将手牌初始化为牌型
        :return:
        """

        # 国士无双
        guo_count = {'E': 0, 'W': 0, 'S': 0, 'N': 0, 'B': 0, 'F': 0, 'Z': 0, '1M': 0, '9M': 0, '1P': 0, '9P': 0,
                     '1S': 0, '9S': 0}
        for tile in self.hidden_set:
            if tile in guo_count.keys():
                if tile not in guo_count:
                    guo_count[tile] = 0
                guo_count[tile] += 1
        if len(self.hidden_set) == 14 and sum(count == 1 for count in guo_count.values()) == 12 and any(
                count == 2 for count in guo_count.values()):
            self.hand_list.append([self.hidden_set])
            self.is_guoshi = True
            return

        # 处理雀头
        for dou_type in self.hidden_count.keys():
            if self.hidden_count[dou_type] >= 2:
                self.hidden_count[dou_type] -= 2
                dfs_split(self.hidden_count.copy(), self.hand_list, res_stack=[[dou_type] * 2])
                self.hidden_count[dou_type] += 2

        if len(self.hand_list) != 0:
            return

        # 七对， 因为优先级低于两杯口所以延后处理
        if len(self.hidden_set) == 14 and all(count == 2 for count in self.hidden_count.values()):
            self.hand_list.append([self.hidden_set])
            self.is_qidui = True
            return

    def check_valid(self):
        for hand in self.hand_list:
            if check_pai(hand, self.cpg_list):
                return True
        return False

    def push_yi(self, yi_name):
        self.yi_infos.append(yi_name)

    # 获取一共多少张宝牌，返回表，里，赤朵拉数
    def get_doras(self):
        dora_count = 0
        ura_dora_count = 0
        doras = [dora_check(dora) for dora in self.maj_data.dora_indicators]
        ura_doras = [dora_check(dora) for dora in self.maj_data.ura_dora_indicators]
        for tile in self.hidden_count.keys():
            if tile in doras:
                dora_count += self.hidden_count[tile]
            if tile in ura_doras:
                ura_dora_count += self.hidden_count[tile]
        return dora_count, ura_dora_count, self.rcount['R5P'] + self.rcount['R5S'] + self.rcount['R5M']

    # 处理非牌型相关役种
    def pre_all_yi(self):
        res_yi = []
        dora, ura_dora, red_dora = self.get_doras()
        for i in range(dora):
            res_yi.append('dora')
        if self.maj_data.is_riichi or self.maj_data.is_double_riichi:
            for i in range(ura_dora):
                res_yi.append('ura_dora')
        for i in range(red_dora):
            res_yi.append('red_dora')

        if self.maj_data.is_double_riichi:
            res_yi.append('double_riichi')
        elif self.maj_data.is_riichi:
            res_yi.append('riichi')
        if self.maj_data.is_first_turn:
            res_yi.append('ippatsu')
        if self.maj_data.is_self_draw and len(self.cpg_list) == 0:
            res_yi.append('menzen_tsumo')
        if self.maj_data.is_on_kang:
            res_yi.append('rinshan')
        if self.maj_data.is_catch_kang:
            res_yi.append('chankan')
        if self.maj_data.is_river_or_sea:
            res_yi.append('haitei')
        return res_yi

    # 计算牌型的符数
    def fu_count(self, hidden_list, cpg_list):
        if self.is_qidui:
            return 25
        fu = 20  # 基础符
        for group in hidden_list:
            # 雀头是否为役牌
            if len(group) == 2:
                tile = group[0]
                if tile in ['Z', 'F', 'B']:
                    fu += 2
        yaojiu_tiles = [
            '1M', '9M', '1S', '9S', '1P', '9P', 'E', 'S', 'W', 'N', 'Z', 'F', 'B'
        ]
        # 处理每个面子
        for group in hidden_list:
            if len(group) >= 3 and group[0] == group[1]:
                base_ke = 4
                if len(group) == 4:
                    base_ke *= 4
                if group[0] in yaojiu_tiles:
                    base_ke *= 2
                fu += base_ke

        for group in hidden_list:
            if len(group) >= 3 and group[0] == group[1]:
                base_ke = 2
                if len(group) == 4:
                    base_ke *= 4
                if group[0] in yaojiu_tiles:
                    base_ke *= 2
                fu += base_ke
        # 门清和和牌方式
        if len(cpg_list) == 0 and not self.maj_data.is_self_draw:
            fu += 10
        elif self.maj_data.is_self_draw:
            fu += 2

        # 听牌类型
        if len(self.tin_set) == 1:
            fu += 2

        # 进位处理（向上取整到十位）
        fu = ((fu + 9) // 10) * 10
        return fu

    # 调用之前请使用split_init
    def calc_yi(self, hidden_list, cpg_list):
        """
        对役满进行判断：
        判断完役满之后，如果满足任意役满条件则退出
        """
        yi_clac_list = []
        if not check_pai(hidden_list, cpg_list):
            return 0
        total_list = hidden_list + cpg_list
        # 幺九牌集
        yaojiu_tiles = [
            '1M', '9M', '1S', '9S', '1P', '9P', 'E', 'S', 'W', 'N', 'Z', 'F', 'B'
        ]
        # 风牌，字牌预处理
        wind_count = {'E': 0, 'W': 0, 'S': 0, 'N': 0}
        zi_count = {'B': 0, 'F': 0, 'Z': 0}
        for tiles in total_list:
            for tile in tiles:
                if tile in wind_count:
                    wind_count[tile] += 1
                if tile in zi_count:
                    zi_count[tile] += 1
        kang_count = 0
        hidden_kang_count = self.maj_data.concealed_kangs
        cpg_kang_count = 0
        hidden_pung_count = self.maj_data.concealed_kangs
        cpg_pung_count = -self.maj_data.concealed_kangs
        # 刻子计数
        for group in hidden_list:
            # 检查是否为刻子或杠（3或4张相同牌）
            if len(group) >= 3 and all(tile == group[0] for tile in group):
                hidden_pung_count += 1

        for group in cpg_list:
            # 检查是否为刻子或杠（3或4张相同牌）
            if len(group) >= 3 and all(tile == group[0] for tile in group):
                cpg_pung_count += 1
                if len(group) == 4:
                    kang_count += 1
        cpg_kang_count = kang_count - hidden_kang_count
        pung_count = hidden_pung_count + cpg_pung_count
        # 顺子计数
        shun_count = 4 - pung_count

        # 首先检查是否清一色（只有一种花色）
        suits = set()
        for group in total_list:
            for tile in group:
                if len(tile) == 2:
                    suits.add(tile[-1])  # 获取花色
                else:
                    suits.add('Z')

        men_tsu = len(cpg_list) == 0

        # 役满判断：
        # 1. 天/地和
        if self.maj_data.is_first_turn_win:
            yi_clac_list.append('tenho')
        # 2. 大四喜/小四喜

        if all([count >= 3 for wind, count in wind_count.items()]):
            yi_clac_list.append('daisushi')
        else:
            for tiles in total_list:
                if len(tiles) == 2 and tiles[0] in wind_count:
                    wind_count[tiles[0]] += 1
            if all([count >= 3 for wind, count in wind_count.items()]):
                yi_clac_list.append('shosushi')

        # 3. 国士无双
        if self.is_guoshi:
            yi_clac_list.append('kokushi')

        # 4. 字一色
        if all(tiles[0] in wind_count.keys() or tiles[0] in zi_count.keys() for tiles in total_list):
            yi_clac_list.append('tsuiso')

        # 5. 大三元
        if all([count >= 3 for zi, count in zi_count.items()]):
            yi_clac_list.append('daisangen')

        # 6. 四暗刻
        if hidden_pung_count == 4:
            for tiles in total_list:
                # 找到和牌
                if self.end_maj == tiles[0]:
                    if len(tiles) == 2:
                        yi_clac_list.append('suankotanki')
                    elif self.maj_data.is_self_draw:
                        yi_clac_list.append('suanko')

        # 7. 九莲宝灯
        if len(suits) == 1 and men_tsu:
            numbers = []
            for group in hidden_list:
                for tile in group:
                    if len(tile) == 2:
                        numbers.append(int(tile[0]))
            # 检查总牌数是否为14张（标准麻将和牌数）
            if len(numbers) == 14:
                numbers.sort()
                jiulian_base = {i: 1 for i in range(1, 10)}
                jiulian_base[1] = 3
                jiulian_base[9] = 3
                jiu_flag = True
                for i in range(1, 10):
                    if numbers.count(i) < jiulian_base[i]:
                        jiu_flag = False
                if jiu_flag:
                    yi_clac_list.append('chuuren')
        # 8. 绿一色
        green_tiles = {
            '2S', '3S', '4S', '6S', '8S',  # 绿色条子
            'F'  # 发字牌
        }
        if all([tile in green_tiles for tiles in hidden_list for tile in tiles]):
            yi_clac_list.append('ryuiso')

        # 9. 四杠子
        if all([len(tiles) == 2 or len(tiles) == 4 for tiles in total_list]):
            yi_clac_list.append('sukantsu')

        # 10. 清老头
        lao_tiles = {
            '1S', '9S', '1P', '9P', '1M', '9M'
        }
        if all([tile in lao_tiles for tiles in hidden_list for tile in tiles]):
            yi_clac_list.append('chinroto')

        if len(yi_clac_list) != 0:
            return True, yi_clac_list
        # 常规役
        yi_clac_list = self.pre_all_yi()

        # 1. 断幺

        if all([tile not in yaojiu_tiles for tiles in hidden_list for tile in tiles]):
            yi_clac_list.append('tanyao')

        # 2. 平和

        if shun_count == 4 and len(self.tin_set) >= 2 and men_tsu:
            yi_clac_list.append('pinfu')

        # 3. 一杯口
        peikou_shun_list = []
        for tiles in hidden_list:
            if tiles[0] != tiles[1]:
                peikou_shun_list.append(tiles[0])
        same_shun_count = len(peikou_shun_list) - len(set(peikou_shun_list))
        if same_shun_count == 2:
            yi_clac_list.append('ryanpeikou')
        if same_shun_count == 1:
            yi_clac_list.append('iipeko')

        # 4. 役牌
        for group in hidden_list:
            if len(group) >= 3 and all(tile == group[0] for tile in group):
                tile = group[0]
                if tile == 'B':
                    yi_clac_list.append("yakuhai_haku")
                elif tile == 'F':
                    yi_clac_list.append("yakuhai_hatsu")
                elif tile == 'Z':
                    yi_clac_list.append("yakuhai_chun")
                elif tile == self.maj_data.current_round:
                    yi_clac_list.append("yakuhai_wind_round")
                elif tile == self.maj_data.self_round:
                    yi_clac_list.append("yakuhai_wind_seat")

        # 5. 一气通贯
        iitsu_set = {
            'M': [False * 3],
            'S': [False * 3],
            'P': [False * 3],
        }
        for group in total_list:
            if group[0] != group[1]:
                pai_suit = group[0][1]
                pai_num = group[0][0]
                if pai_num in [1, 4, 7]:
                    iitsu_set[pai_suit][pai_num // 3] = True
        if any(all(suit_set) for suit_set in iitsu_set.values()):
            yi_clac_list.append("ittsu")

        # 6. 三色同顺
        chow_starts = {'M': set(), 'S': set(), 'P': set()}

        for group in total_list:
            if group[0] == group[1]:
                continue
            suit = group[0][1]
            chow_starts[suit].add(group[0][0])

        # 检查三种花色是否有相同起始数字的顺子
        common_starts = chow_starts['M'] & chow_starts['S'] & chow_starts['P']
        if len(common_starts) > 0:
            yi_clac_list.append("sanshoku")

        # 7. 混全/纯全带幺九
        if all(any([tile in yaojiu_tiles for tile in group]) for group in total_list) and not self.is_qidui:
            if 'Z' in suits:
                yi_clac_list.append("chanta")
            else:
                yi_clac_list.append("junchan")

        # 8. 三杠子
        if kang_count == 3:
            yi_clac_list.append("sankantsu")

        # 9. 对对和
        if pung_count == 4:
            yi_clac_list.append("toitoi")

        # 10. 三暗刻
        if hidden_pung_count == 3:
            yi_clac_list.append("sananko")

        # 11. 小三元
        for tiles in total_list:
            if len(tiles) == 2 and tiles[0] in zi_count:
                zi_count[tiles[0]] += 1
        if all([count >= 3 for zi, count in zi_count.items()]):
            yi_clac_list.append('shosangen')

        # 12. 七对
        print('isqidui', self.is_qidui)
        if self.is_qidui:
            yi_clac_list.append('qiedui')

        # 13. 混一色
        if len(suits) == 2 and 'Z' in suits:
            yi_clac_list.append('honitsu')

        if len(suits) == 1:
            yi_clac_list.append('chinitsu')

        return False, yi_clac_list

    def get_score_info(self):
        score_max = 0
        yi_info_max = {}
        han_max = 0
        fu_max = 0
        hand_max = []
        yi_man = False
        for hand in self.hand_list:
            # all_list = hand + self.cpg_list
            self.tin_set = self.check_tin()
            yiman, yi = self.calc_yi(hand, self.cpg_list)
            yi_info = {}
            han = 0
            for i in yi:
                now_han = [yi_list, yi_full_list][yiman][i][1] + [0, -1][len(self.cpg_list) != 0 and i in men_tsu_full]
                han += now_han
                if i in yi_info.keys():
                    yi_info[i][1] += 1
                else:
                    yi_info[i] = [[yi_list, yi_full_list][yiman][i][0], now_han]
            fu = self.fu_count(hand, self.cpg_list)
            score = calculate_points(fu, han, self.maj_data.is_dealer, yiman)
            if score > score_max:
                score_max = score
                yi_info_max = yi_info
                han_max = han
                fu_max = fu
                hand_max = hand
                yi_man = yiman

        # 将handmax以其中数组长度从大到小排序
        hand_max.sort(key=lambda x: len(x), reverse=True)

        res = {
            'hand_tile': hand_max,
            'cpg_tile': self.cpg_list,
            'total_tile': hand_max + self.cpg_list,
            'yiman': yi_man,
            'totalScore': score_max,
            'han': han_max,
            'fu': [fu_max, 0][yi_man],
            'details': [[yi_info[0], f'{yi_info[1]}{["番", "倍役满"][yi_man]}'] for yi_info in yi_info_max.values()]
            # 'details': [f'{yi_info[1]}{["番", "倍役满"][yi_man]}' for yi_info in yi_info_max.values()]
        }
        return res
        # print('hand:', hand_max)
        # print('info', list(yi_info_max.values()))
        # print(f'{han_max}{["番", "倍役满"][yi_man]}\nscore: {score_max}')

# winning_hand = ['E', 'E', 'E', 'S', 'S', 'S', 'W', 'W', 'W', 'B', 'B', 'Z', 'Z', 'Z']
# winning_hand = ['1M', '9M', '1S', '9S', '1P', '9P', 'E', 'W', 'S', 'N', 'B', 'F', 'Z', '1M']
# winning_hand = [
#     '1M', '1M', '1M',
#     '2M', '3M', '4M',
#     '5M', '6M', '7M',
#     '8M', '9M', '9M',
#     '9M', '2M']  # 额外的2万

# winning_hand = [
#     '2S', '2S', '2S',  # 绿色刻子
#     '2S', '3S', '4S',  # 注意:5S不是绿色牌
#     '6S', '6S', '6S',
#     '8S', '8S',
#     'F', 'F', 'F'
# ]

# winning_hand = ['1M', '2M', '3M', '1P', '2P', '2P', '3P', '3P', '1S', '1S', '1S', '2S', '3S', '1P']

# winning_hand = ['3M', '3M', '3M', '2P', '3P', '4P', '5P', '6P', '1S', '1S', '1S', '2S', '3S', '1P']


# print(f"input={winning_hand}")
# form_data = FormData(hand_tiles=winning_hand, is_riichi=True, dora_indicators=['9S'], is_self_draw=True, is_first_turn=True)  # 创建 FormData 对象
# hand_maj_set = HandMajSet(form_data)  # 传递 FormData 对象
# # print(hand_maj_set.calculate_points(fu=110, han=2, is_dealer=True))
# # print(1)
# print("hand_list", hand_maj_set.hand_list)
# hand_maj_set.get_score()
