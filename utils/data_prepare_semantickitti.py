import pickle, yaml, os, sys
import numpy as np
from os.path import join, exists, dirname, abspath
from sklearn.neighbors import KDTree
import os

TMPDIR = '' # os.environ["TMPDIR"]

BASE_DIR = dirname(abspath(__file__))
ROOT_DIR = dirname(BASE_DIR)
sys.path.append(BASE_DIR)
sys.path.append(ROOT_DIR)
from helper_tool import DataProcessing as DP

data_config = os.path.join(BASE_DIR, 'semantic-kitti.yaml')
DATA = yaml.safe_load(open(data_config, 'r'))
remap_dict = DATA["learning_map"]
max_key = max(remap_dict.keys())
remap_lut = np.zeros((max_key + 100), dtype=np.int32)
remap_lut[list(remap_dict.keys())] = list(remap_dict.values())

grid_size = 0.06
dataset_path = TMPDIR + 'data/semantic_kitti/dataset/sequences'
output_path = TMPDIR + 'data/semantic_kitti/dataset/sequences' + '_' + str(grid_size)
seq_list = np.sort(os.listdir(dataset_path))
count1 = 0
count2 = 0
count3 = 0
for seq_id in seq_list:
    print('sequence' + seq_id + ' start')
    seq_path = join(dataset_path, seq_id)
    seq_path_out = join(output_path, seq_id)
    pc_path = join(seq_path, 'velodyne')
    pc_path_out = join(seq_path_out, 'velodyne')
    KDTree_path_out = join(seq_path_out, 'KDTree')
    os.makedirs(seq_path_out) if not exists(seq_path_out) else None
    os.makedirs(pc_path_out) if not exists(pc_path_out) else None
    os.makedirs(KDTree_path_out) if not exists(KDTree_path_out) else None

    if int(seq_id) < 10:
        label_path = join(seq_path, 'labels')
        label_path_out = join(seq_path_out, 'labels')
        os.makedirs(label_path_out) if not exists(label_path_out) else None
        scan_list = np.sort(os.listdir(pc_path))
        for scan_id in scan_list:
            """
            if int(scan_id[:6]) % 500 == 0:
                print(scan_id)
            """
            points = DP.load_pc_kitti(join(pc_path, scan_id))
            labels = DP.load_label_kitti(join(label_path, str(scan_id[:-4]) + '.label'), remap_lut)
            sub_points, sub_labels = DP.grid_sub_sampling(points, labels=labels, grid_size=grid_size)
            if sub_points.shape[0] < 4096*3:
                print(f'SEQ {seq_id} NUM {scan_id} < 4096*3')
                print(f'Original length is {points.shape[0]} and processed length is {sub_points.shape[0]}')
                count1 += 1
            if sub_points.shape[0] < 4096*4:
                print(f'SEQ {seq_id} NUM {scan_id} < 4096*4')
                print(f'Original length is {points.shape[0]} and processed length is {sub_points.shape[0]}')
                count2 += 1
            if sub_points.shape[0] < 4096*5:
                print(f'SEQ {seq_id} NUM {scan_id} < 4096*5')
                print(f'Original length is {points.shape[0]} and processed length is {sub_points.shape[0]}')
                count3 += 1
            search_tree = KDTree(sub_points)
            KDTree_save = join(KDTree_path_out, str(scan_id[:-4]) + '.pkl')
            np.save(join(pc_path_out, scan_id)[:-4], sub_points)
            np.save(join(label_path_out, scan_id)[:-4], sub_labels)
            with open(KDTree_save, 'wb') as f:
                pickle.dump(search_tree, f)
            if seq_id == '08':
                proj_path = join(seq_path_out, 'proj')
                os.makedirs(proj_path) if not exists(proj_path) else None
                proj_inds = np.squeeze(search_tree.query(points, return_distance=False))
                proj_inds = proj_inds.astype(np.int32)
                proj_save = join(proj_path, str(scan_id[:-4]) + '_proj.pkl')
                with open(proj_save, 'wb') as f:
                    pickle.dump([proj_inds], f)
    else:
        proj_path = join(seq_path_out, 'proj')
        os.makedirs(proj_path) if not exists(proj_path) else None
        scan_list = np.sort(os.listdir(pc_path))
        for scan_id in scan_list:
            """
            if int(scan_id[:6]) % 500 == 0:
                print(scan_id)
            """
            points = DP.load_pc_kitti(join(pc_path, scan_id))
            sub_points = DP.grid_sub_sampling(points, grid_size=0.06)
            if sub_points.shape[0] < 4096*3:
                print(f'SEQ {seq_id} NUM {scan_id} < 4096*3')
                print(f'Original length is {points.shape[0]} and processed length is {sub_points.shape[0]}')
                count1 += 1
            if sub_points.shape[0] < 4096*4:
                print(f'SEQ {seq_id} NUM {scan_id} < 4096*4')
                print(f'Original length is {points.shape[0]} and processed length is {sub_points.shape[0]}')
                count2 += 1
            if sub_points.shape[0] < 4096*5:
                print(f'SEQ {seq_id} NUM {scan_id} < 4096*5')
                print(f'Original length is {points.shape[0]} and processed length is {sub_points.shape[0]}')
                count3 += 1
            search_tree = KDTree(sub_points)
            proj_inds = np.squeeze(search_tree.query(points, return_distance=False))
            proj_inds = proj_inds.astype(np.int32)
            KDTree_save = join(KDTree_path_out, str(scan_id[:-4]) + '.pkl')
            proj_save = join(proj_path, str(scan_id[:-4]) + '_proj.pkl')
            np.save(join(pc_path_out, scan_id)[:-4], sub_points)
            with open(KDTree_save, 'wb') as f:
                pickle.dump(search_tree, f)
            with open(proj_save, 'wb') as f:
                pickle.dump([proj_inds], f)

print(f'After preprocessing, {count1} PCs are smaller than 4096*3, {count2} PCs are smaller than 4096*4, {count3} PCs are smaller than 4096*5.')
