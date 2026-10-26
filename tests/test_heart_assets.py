"""Integrity checks for licensed anatomical geometry and the preserved hero."""
import base64
import hashlib
import json
import re
import struct
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'app_and_ml/assets/heart'


class HeartAssetsTests(unittest.TestCase):
    def test_reference_hash_and_mesh_integrity(self):
        data = (ASSETS / 'models/heart.glb').read_bytes()
        manifest = json.loads((ASSETS / 'models/upstream-manifest.json').read_text())
        self.assertEqual(hashlib.sha256(data).hexdigest(), manifest['runtime']['sha256'])
        magic, version, length = struct.unpack_from('<III', data)
        self.assertEqual((magic, version, length), (0x46546C67, 2, len(data)))
        json_length = struct.unpack_from('<I', data, 12)[0]
        model = json.loads(data[20:20 + json_length])
        offset = 28 + json_length
        self.assertEqual(len(model['nodes']), 11)
        for node in model['nodes']:
            primitive = model['meshes'][node['mesh']]['primitives'][0]
            for name in ['POSITION', 'NORMAL']:
                accessor = model['accessors'][primitive['attributes'][name]]
                view = model['bufferViews'][accessor['bufferView']]
                values = np.ndarray((accessor['count'], 3), dtype='<f4', buffer=data,
                                    offset=offset + view.get('byteOffset', 0) + accessor.get('byteOffset', 0),
                                    strides=(view.get('byteStride', 12), 4))
                self.assertTrue(np.isfinite(values).all(), node['name'])
            positions = model['accessors'][primitive['attributes']['POSITION']]['count']
            accessor = model['accessors'][primitive['indices']]
            view = model['bufferViews'][accessor['bufferView']]
            indices = np.frombuffer(data, dtype='<u4', count=accessor['count'],
                                    offset=offset + view.get('byteOffset', 0) + accessor.get('byteOffset', 0))
            self.assertLess(int(indices.max()), min(positions, 65536), node['name'])
            self.assertEqual(len(indices) % 3, 0)

    def test_extra_source_geometry_and_valve_coverage(self):
        payload=(ASSETS / 'models/cardiac-extras.json').read_bytes()
        manifest=json.loads((ASSETS / 'models/cardiac-extras-manifest.json').read_text())
        self.assertEqual(hashlib.sha256(payload).hexdigest(),manifest['runtime_sha256'])
        meshes=json.loads(payload)
        self.assertEqual(len(meshes),17)
        page = (ASSETS / 'index.html').read_text()
        details = json.loads(re.search(r'const partDetails = (\{.*?\});', page, re.S)[1])
        self.assertEqual(len(details), 28)
        self.assertTrue({mesh['id'] for mesh in meshes}.issubset(details))

        self.assertEqual({m['id'] for m in meshes if m['internal']},
                         {'tricuspid-valve','mitral-valve','aortic-valve','pulmonary-valve'})
        for mesh, record in zip(meshes,manifest['structures']):
            positions=np.frombuffer(base64.b64decode(mesh['positions']),dtype='<f4').reshape(-1,3)
            normals=np.frombuffer(base64.b64decode(mesh['normals']),dtype='<f4').reshape(-1,3)
            indices=np.frombuffer(base64.b64decode(mesh['indices']),dtype='<u2')
            self.assertEqual(len(positions),record['vertices'])
            self.assertEqual(len(indices),record['triangles']*3)
            self.assertEqual(positions.shape,normals.shape)
            self.assertTrue(np.isfinite(positions).all() and np.isfinite(normals).all())
            self.assertLess(int(indices.max()),len(positions))
            self.assertGreater(len(record['source_elements']),0)

    def test_original_top_geometry_is_preserved_separately(self):
        before = (ROOT / 'docs/reference/heart-before-anatomy-upgrade.html').read_text()
        original = before[before.index('function meshData('):before.index('// Upload meshes once.')]
        current = (ASSETS / 'index.html').read_text()
        without_comments = lambda text: re.sub(r'//[^\n]*', '', text)
        self.assertIn(without_comments(original), without_comments(current))
        self.assertIn('makePointCloud(topAnatomy,42000)', current)
        self.assertIn("decodeReferenceModel('__MODEL_BASE64__')", current)


if __name__ == '__main__':
    unittest.main()
