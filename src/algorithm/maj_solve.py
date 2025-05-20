from src.global_data.global_data import GlobalData, ScanCluster
import os

def solve_maj_pic_index(uuid: str, pic: any):
    scan_cluster = ScanCluster(uuid, pic)
    GlobalData.push_scan_cluster(scan_cluster)
    scan_cluster.start_clust()
    try:
        os.remove(pic.name)
        print(f'{pic.name} has been deleted.')
    except Exception as e:
        print(f'Error deleting file {pic.name}: {e}')
    
    print('finish solve_maj_pic_index')