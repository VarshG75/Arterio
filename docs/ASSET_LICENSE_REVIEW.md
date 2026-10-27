# Website asset review — October 26, 2026

The deployed code paths in `views/heart.py`, `assets/heart/index.html` and `views/architecture.py` were checked against the bundled assets. This is an attribution and source-license review, not an independent determination of every upstream contributor's rights.

| Asset | Published source terms | Current handling |
| --- | --- | --- |
| `heart-diagram-en.svg` | ZooFari, [source and author notice](https://commons.wikimedia.org/wiki/File:Heart_diagram-en.svg), CC BY-SA 3.0 | Original SVG preserved; grayscale display disclosed and licensed under CC BY-SA 3.0. Title, author, source and license links appear in the viewer. |
| `heart-chambers-valves.svg` | Wapcaplet and Yaddah, [source and author notice](https://commons.wikimedia.org/wiki/File:Diagram_of_the_human_heart.svg), CC BY-SA 3.0 option | Same handling as above; credits retained. |
| Heart GLB and extra meshes | BodyParts3D, [official archive license](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html), CC BY 4.0 | Required dataset credit and license link retained. OrganUI preparation, display changes and extra-mesh processing documented. Source hashes checked by the asset tests. |
| Opening point cloud and signal drawings | Procedural application geometry and inline SVG paths | No reference photograph is embedded. The source model and reference diagrams have separate notices. |
| Ariana Bik JPG references supplied in chat | Redistribution permission was not established in this review | Used only for visual comparison; none are in the tracked project or embedded in the website. No license is inferred from being supplied as a reference. |

The [CC BY-SA 3.0 terms](https://creativecommons.org/licenses/by-sa/3.0/) require attribution, a license link and the same license for adaptations. The viewer and reference attribution file now explicitly identify the grayscale display change. These image notices apply separately from the application's MIT license. Third-party names in source credits are retained as attribution.

Orchid Security and Terminal Industries were layout/motion references. Their images, logos, text and source code are not bundled. Google Fonts is an existing external font dependency; it is not a reference-image source. The dataset and saved model are outside this image review and were not scanned.
