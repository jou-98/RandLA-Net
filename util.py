import numpy as np
import open3d as o3d

BIN_DIR = './bin/'
LABELs_DIR = './labels/'

CLASSES = {0:"unlabeled", 1 : "outlier", 11: "bicycle", 15: "motorcycle",\
        30: "person", 31: "bicyclist", 32: "motorcyclist", 40: "road",\
        44: "parking", 48: "sidewalk", 49: "other-ground",80: "pole",\
        81: "traffic-sign"}


def render_color(pc,label,ply_path='./00_001000_colored.ply'):
    labels = np.unique(label)
    print(np.unique(label,return_counts=True))
    colors = dict()
    for i in labels:
        color = list(np.random.choice(range(100), size=3)/100)
        colors[i] = color
    #print(colors)
    rgb = np.zeros((pc.shape[0],3))
    for i in labels:
        label_pos = np.where(label==i)
        if not i in CLASSES:
            continue
        rgb[label_pos] = colors[i]
        print(f'Colour of class {CLASSES[i]} is \
        [{colors[i][0]*255},{colors[i][1]*255},{colors[i][2]*255}]')
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pc)
    # print(rgb.shape())
    pcd.colors = o3d.utility.Vector3dVector(rgb)
    o3d.io.write_point_cloud(ply_path, pcd) 
    
    
    

# Reads a .bin file into numpy array and (optionally) saves it as a ply file
def read_pc(path='./dataset/sequences/00/velodyne/001000.bin',dim=4):
    scan = np.fromfile(path, dtype=np.float32)
    scan = scan.reshape((-1, dim))     
    return scan[:,:3]

def save_pc(array,ply_path='./00_001000.ply'):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(array[:,:3])
    o3d.io.write_point_cloud(ply_path, pcd) 


# Reads a .label file into numpy array
def read_label(path='./labels/00_000143.label',dim=2):
    labels = np.fromfile(path, dtype=np.uint16).reshape((-1,dim))
    labels = labels[:,0]
    #print(np.unique(labels,return_counts=True))
    return labels

# Merges point array and label array
# Possible to use either combination of seq# and frame# (e.g. seq=00, frame=000143)
# or individual paths
def get_pc_and_label(use_seq_frame=True,seq='00',frame='000143',\
    bin_path=None,label_path=None):
    if use_seq_frame:
        bin_path = BIN_DIR+seq+'_'+frame+'.bin'
        label_path = LABEL_DIR+seq+'_'+frame+'.label'
    pts = read_pc(path=bin_path,save_ply=False)
    labels = read_label(path=label_path)
    labels = labels.reshape((-1,1))
    ret = np.concatenate((pts,labels),axis=1)
    return ret 

# Renders a point cloud in black and white, reads either bin file or ply file 
def render_binary(use_ply=False,bin_path='./bin/00_000143.bin',ply_path=None,\
    label_path='./labels/00_000143.label',render_path='./binary_test.ply'):

    labels = read_label(path=label_path)
    labels = labels.reshape((-1,1))
    rgb = np.concatenate((labels,labels,labels),axis=1)
    pc = []
    if not use_ply and bin_path is not None:
        pc = read_pc(path=bin_path)
    elif ply_path is not None:
        pass
    else:
        print(f'function call: render_binary: please set either bin_path or ply_path')
    rgb = np.concatenate((labels,labels,labels),axis=1)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pc)
    pcd.colors = o3d.utility.Vector3dVector(rgb)
    o3d.io.write_point_cloud(render_path, pcd) 

# Needs to read bin files from the original dataset to get intensity value
def read_pc_orig(path='./bin/00_000143.bin', save_ply=True, ply_path='./test.ply',\
    rgb=False):
    scan = np.fromfile(path, dtype=np.float32)
    scan = scan.reshape((-1, 4))# if rgb else scan.reshape((-1, 3))
    if rgb: intensity = scan[:,3].reshape((-1,1))
    scan = scan[:,:3]
    if rgb: colors = np.concatenate((intensity,intensity,intensity),axis=1)
    if save_ply and ply_path is not None:
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(scan)
        if rgb: pcd.colors = o3d.utility.Vector3dVector(colors)

        o3d.io.write_point_cloud(ply_path, pcd)        
    return scan