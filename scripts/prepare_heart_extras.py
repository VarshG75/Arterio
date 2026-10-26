"""Prepare source-mapped cardiac additions from verified BodyParts3D OBJ files.

Input: /tmp/arterio-heart-obj downloaded from the official IS-A 99% archive.
No source geometry is stretched. Vessel segments are clipped at a display boundary.
"""
import base64
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('/tmp/arterio-heart-obj')
CENTER = np.array([21.5438, -113.22495, 1245.64])
GROUPS = {
    'coronary-sinus': ('Coronary sinus', ['FJ2655'], False),
    'great-cardiac-vein': ('Great cardiac vein', ['FJ2656'], False),
    'middle-cardiac-vein': ('Middle cardiac vein', ['FJ2678','FJ2679','FJ2680','FJ2681','FJ2682','FJ2683','FJ2684','FJ2685','FJ2686','FJ2687','FJ2688','FJ2689','FJ2690','FJ2691'], False),
    'tricuspid-valve': ('Tricuspid valve', ['FJ2421','FJ2433','FJ2436'], True),
    'mitral-valve': ('Mitral valve', ['FJ2420','FJ2432'], True),
    'aortic-valve': ('Aortic valve', ['FJ2426','FJ2431','FJ2435'], True),
    'pulmonary-valve': ('Pulmonary valve', ['FJ2417','FJ2427','FJ2434'], True),
    'inferior-vena-cava': ('Inferior vena cava', ['FJ3441'], False),
    'right-superior-pulmonary-vein': ('Right superior pulmonary vein', ['FJ3020'], False),
    'right-inferior-pulmonary-vein': ('Right inferior pulmonary vein', ['FJ3040'], False),
    'left-superior-pulmonary-vein': ('Left superior pulmonary vein', ['FJ2925'], False),
    'left-inferior-pulmonary-vein': ('Left inferior pulmonary vein', ['FJ2944'], False),
    'brachiocephalic-trunk': ('Brachiocephalic trunk', ['FJ3417'], False),
    'left-common-carotid': ('Left common carotid artery', ['FJ3483'], False),
    'left-subclavian': ('Left subclavian artery', ['FJ3479'], False),
    'right-pulmonary-artery': ('Right pulmonary artery', ['FJ3019'], False),
    'left-pulmonary-artery': ('Left pulmonary artery', ['FJ2924'], False),
}

def read_obj(path):
    vertices, triangles = [], []
    for line in path.read_text().splitlines():
        fields = line.split()
        if fields and fields[0] == 'v': vertices.append(list(map(float,fields[1:4])))
        elif fields and fields[0] == 'f':
            indices = [int(v.split('/')[0])-1 for v in fields[1:]]
            for i in range(1,len(indices)-1): triangles.append([indices[0],indices[i],indices[i+1]])
    v=(np.asarray(vertices)-CENTER)[:,[0,2,1]]*np.array([.02,.02,-.02])
    return v,np.asarray(triangles)


def clip_mesh(vertices, faces, bounds):
    """Cut triangles at planes, weld seams and retain the main connected segment.

    No caps or new anatomical shapes are introduced at truncated vessel ends.
    """
    result_v, result_f, lookup = [], [], {}
    for face in faces:
        polygon=[vertices[i] for i in face]
        for axis,(low,high) in enumerate(bounds):
            for limit,direction in [(low,1),(high,-1)]:
                clipped=[]
                for i,a in enumerate(polygon):
                    b=polygon[(i+1)%len(polygon)]
                    ina=(a[axis]-limit)*direction>=0
                    inb=(b[axis]-limit)*direction>=0
                    if ina: clipped.append(a)
                    if ina!=inb:
                        clipped.append(a+(b-a)*(limit-a[axis])/(b[axis]-a[axis]))
                polygon=clipped
                if not polygon:break
            if not polygon:break
        indices=[]
        for point in polygon:
            key=tuple(np.round(point,6))
            if key not in lookup:
                lookup[key]=len(result_v);result_v.append(point)
            indices.append(lookup[key])
        for i in range(1,len(indices)-1):
            tri=[indices[0],indices[i],indices[i+1]]
            if len(set(tri))==3: result_f.append(tri)
    if not result_f:return np.empty((0,3)),np.empty((0,3),dtype=int)
    v,f=np.asarray(result_v),np.asarray(result_f)
    parent=list(range(len(v)))
    def find(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]];i=parent[i]
        return i
    for a,b,c in f:
        parent[find(b)]=find(a);parent[find(c)]=find(a)
    roots=np.array([find(int(a)) for a in f[:,0]])
    labels,counts=np.unique(roots,return_counts=True)
    f=f[roots==labels[np.argmax(counts)]]
    return v,f


def encode(array, dtype):
    return base64.b64encode(np.asarray(array,dtype=dtype).tobytes()).decode()


def main():
    data=[]
    manifest={'dataset':'BodyParts3D 4.0', 'archive':'isa_BP3D_4.0_obj_99.zip',
              'source':'https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip',
              'license':'CC BY 4.0', 'transform':'[x,z,-y] at scale .02 after subtracting upstream center',
              'verification':'Official ZIP central-directory CRC checked per downloaded file; full archive checksum not checked.',
              'display_bounds':{'x':[-1.35,1.35],'y':[-1.45,1.8],'z':[-1.2,1.4]}, 'vessel_processing':'Plane-clipped triangles; largest connected component per source element; pulmonary artery proximal bounds x±1.05, y .1–1.35, z -1.1–.7', 'structures':[]}
    for id,(name,ids,internal) in GROUPS.items():
        all_v, all_f, records = [], [], []
        total=0
        for source_id in ids:
            path=SOURCE/(source_id+'.obj')
            if not path.exists(): raise FileNotFoundError(path)
            v,f=read_obj(path)
            if not internal:
                bounds=[(-1.35,1.35),(-1.45,1.8),(-1.2,1.4)]
                if id.endswith('pulmonary-artery'):
                    bounds=[(-1.05,1.05),(.10,1.35),(-1.1,.7)]
                v,f=clip_mesh(v,f,bounds)
            if not len(f): continue
            used, inverse=np.unique(f,return_inverse=True)
            v=v[used];f=inverse.reshape(-1,3)
            all_v.append(v);all_f.append(f+total);total+=len(v)
            records.append({'id':source_id,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        if not all_v: raise ValueError('No source geometry inside cardiac bounds: '+id)
        v=np.concatenate(all_v);f=np.concatenate(all_f)
        normals=np.zeros_like(v)
        face_normals=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
        for j in range(3):np.add.at(normals,f[:,j],face_normals)
        normals/=np.maximum(np.linalg.norm(normals,axis=1,keepdims=True),1e-12)
        if len(v)>65535:raise ValueError('16-bit vertex limit: '+id)
        data.append({'id':id,'name':name,'internal':internal,'positions':encode(v,'<f4'),'normals':encode(normals,'<f4'),'indices':encode(f,'<u2')})
        manifest['structures'].append({'id':id,'name':name,'internal':internal,'vertices':len(v),'triangles':len(f),'source_elements':records})
        print(id,len(v),len(f))
    out=ROOT/'app_and_ml/assets/heart/models'
    payload=json.dumps(data,separators=(',',':'))
    (out/'cardiac-extras.json').write_text(payload)
    manifest['runtime_sha256']=hashlib.sha256(payload.encode()).hexdigest()
    (out/'cardiac-extras-manifest.json').write_text(json.dumps(manifest,indent=2))

if __name__=='__main__':main()
