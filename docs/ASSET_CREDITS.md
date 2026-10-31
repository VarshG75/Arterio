# Asset credits and licenses

Application code uses the MIT license. Third-party materials retain their own source terms.

| Asset | Source and license | Use |
| --- | --- | --- |
| Heart GLB and additional anatomical meshes | BodyParts3D, [official license](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html), CC BY 4.0 | Anatomical atlas with adapted display proportions. Preparation and mesh mappings are documented in the model attribution files. |
| `heart-diagram-en.svg` | ZooFari, [source](https://commons.wikimedia.org/wiki/File:Heart_diagram-en.svg), CC BY-SA 3.0 | Grayscale display adaptation with source, author and license links in the viewer. |
| `heart-chambers-valves.svg` | Wapcaplet and Yaddah, [source](https://commons.wikimedia.org/wiki/File:Diagram_of_the_human_heart.svg), CC BY-SA 3.0 option | Grayscale display adaptation with source, author and license links in the viewer. |

The [CC BY-SA 3.0 terms](https://creativecommons.org/licenses/by-sa/3.0/) apply to diagram adaptations separately from application code. Third-party attribution names are retained to satisfy the source terms.

Detailed notices:

- [Model attribution](../app_and_ml/assets/heart/models/ATTRIBUTION.md)
- [Diagram attribution](../app_and_ml/assets/heart/references/ATTRIBUTION.md)
- [Dataset source](DATASET_SOURCE.md)

The opening point cloud and signal drawings are procedural application graphics. Google Fonts supplies Inter, Newsreader and JetBrains Mono through the stylesheet import.

To rebuild the supplementary meshes, extract the required OBJ files from the official BodyParts3D IS-A 99% archive. With the project virtual environment active, run:

```sh
python scripts/prepare_heart_extras.py --source-dir "path/to/obj-files"
```

The script writes the supplementary mesh payload and source manifest. The application uses the bundled output and does not need these OBJ files at runtime.
