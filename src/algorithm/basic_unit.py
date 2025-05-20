from typing import Tuple, List

class UnionFind:
    def __init__(self, size):
        # 初始化父节点和大小
        self.parent = [i for i in range(size)]
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
            self.parent[rootQ] = rootP


    def connected(self, p, q):
        # 判断两个元素是否在同一集合
        return self.find(p) == self.find(q)
