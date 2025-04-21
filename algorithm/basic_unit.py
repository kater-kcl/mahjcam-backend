from typing import Tuple, List

class UnionFind:
    def __init__(self, size):
        # 初始化父节点和大小
        self.parent = [i for i in range(size)]
        self.rank = [1] * size

    def find(self, p):
        # 查找根节点，同时进行路径压缩
        if self.parent[p] != p:
            self.parent[p] = self.find(self.parent[p])  # 路径压缩
        return self.parent[p]

    def union(self, p, q):
        # 合并两个集合
        rootP = self.find(p)
        rootQ = self.find(q)

        if rootP != rootQ:
            # 按秩合并
            if self.rank[rootP] > self.rank[rootQ]:
                self.parent[rootQ] = rootP
            elif self.rank[rootP] < self.rank[rootQ]:
                self.parent[rootP] = rootQ
            else:
                self.parent[rootQ] = rootP
                self.rank[rootP] += 1

    def connected(self, p, q):
        # 判断两个元素是否在同一集合
        return self.find(p) == self.find(q)

def convex_hull(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    计算点集的凸包，使用 Graham 扫描算法。
    """
    points = sorted(points)

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]

def dot(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
    """
    计算两个向量的点积。
    """
    return v1[0] * v2[0] + v1[1] * v2[1]