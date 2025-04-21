import threading
from algorithm import pic_cluster
from global_data.maj_entity import MajEntity, MajRect
from typing import Dict, List

class ScanCluster:
    _lock = threading.Lock()

    def __init__(self, uuid: str, pic: any):
        self.uuid = uuid
        self.pic = pic
        self.clust_finished = False
        self.finished = False
        self.result: List[MajRect] = []

    def get_scan_id(self):
        return self.uuid

    def get_pic(self):
        return self.pic

    def set_result(self, result: List[MajRect]):
        self.result = result
        self.finished = True

    def get_result(self) -> List[MajRect]:
        return self.result

    def is_finished(self):
        return self.finished
    
    def start_clust(self):
        clustering_thread = threading.Thread(target=pic_cluster.pic_2_rect_info, args=(self.uuid, self.pic, self.set_result))
        clustering_thread.start()


class GlobalData:

    __scan_clusters: Dict[str, ScanCluster] = {}

    @staticmethod
    def get_scan_cluster(rid):
        return GlobalData.__scan_clusters.get(rid)

    @staticmethod
    def push_scan_cluster(scan_cluster: ScanCluster):
        GlobalData.__scan_clusters[scan_cluster.get_scan_id()] = scan_cluster
        return scan_cluster
    

