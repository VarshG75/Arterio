# Local source record

The user supplied a recovered HTML heart experience and handoff documents. Their instructions were treated as reference context. The current request to remove circular portal rings supersedes the older brief's instruction to preserve them. No commit was made; the exact supplied HTML is retained at `reference/heart-original.html` as a reversible baseline.

Original HTML SHA-256: de35217f881e286eda8469dfbe43ff3c779fb523b327226c3367faecd28f3efd. The adapted runnable copy is `app_and_ml/assets/heart/index.html`. Changes include ARTERIO branding, ring removal, sourced circulation chapter, chapter navigation, structure selection and keyboard controls. Original historical completeness and anatomical accuracy are not certified.

SVG references remain unchanged. Their separate CC BY-SA attribution is in `app_and_ml/assets/heart/references/ATTRIBUTION.md`; those assets are diagrams, not recovered 3D meshes.

The pasted technical handoffs were audited against the current code. Their descriptions of disconnected ingestion, clinical calibration, APG inference and performance were not assumed true. The report was condensed into an implementation-grounded brief and resume drafts. The original training script is retained separately; the legacy saved model was not overwritten or loaded.

The Miro invitation could not be accessed by the web tool, so no board content was used.


## Anatomical atlas and integrated layout update

The pre-upgrade page is retained at `reference/heart-before-anatomy-upgrade.html`. At the user's direction, the original procedural TOP heart is retained; only the lower solid atlas uses the BodyParts3D mesh. Later steering requested a more centered, slightly larger top heart; that changes only its uniform display transform, not its geometry.

Lower atlas source: `organui/heart-3d`, pinned revision `c72ce6654ff8e282942f97750d3104f55ef4fc3d`, asset `public/models/heart.glb`. The 2,524,400-byte download hashes to `b80a727d022a4ab07ccfcf15caccc228eaccb6d69ec0e72923324946ac35a946`, matching its pinned manifest. Current BodyParts3D CC BY 4.0 terms were checked at the official archive. The GLB is unmodified; ARTERIO deinterleaves its attributes into WebGL buffers and changes display materials only. Attribution and known source omissions accompany the asset and appear in the site's reference dialog.

The full-page anatomy route retains a rendering iframe internally for Streamlit compatibility, styled to fill the viewport. It shares the parent site's scroll and navigation instead of exposing a small nested viewer. This uses trusted local code and no user-supplied executable HTML. The upload fix narrows the global font rule, preserving Streamlit's icon font, and updates dropzone selectors to match the current section element.


## Recording, anatomy coverage and motion refinement

Fourteen additional source-mapped structures from the official BodyParts3D 4.0 archive extend the lower model to 25 selectable structures. Their source IDs, CRC verification scope and SHA-256 records are in the extras manifest and asset attribution. Uniform display transforms preserve source proportions; an oblique opening view gives the lower heart a narrower silhouette. The four valve assemblies and ventricular cavities isolate on selection. Major structures are covered across this model and section 02's labeled cross section; microscopic anatomy and distal vessel networks are incomplete. The supplied Ariana Bik photographs informed visual comparison only and are not redistributed.

Orchid Security and Terminal Industries were reviewed as motion/layout references. The chapter sequence uses continuous vertical translation and eased chapter jumps, with reduced-motion handling. Section 02 embeds its actual cited SVG in grayscale. Cohort charts use explicitly labeled simulated data, while the pipeline animation illustrates processing without asserting live measurements. Recording guidance recommends 1080p/60 FPS rather than treating those settings as a validated minimum or accepting screen recordings as optical capture.


## Capture and atlas revision

The v3/v4 handoffs were treated as implementation context. Conflicting trims use 2 seconds at entry and 1 second at exit; the red lower threshold is 30. The live and array APIs share a 25-second cap. Unsupported claims about a universal 20-second clinical standard, guaranteed beat counts, thermal timing, blanching from brightness and attenuated confidence intervals were replaced with accurate protocol and quality wording. PCHIP, SOS filtering, Savitzky–Golay derivatives, foot-referenced ratios and beat-template comparison are implemented. Values are not clipped into clinical-looking ranges.

The coronary sinus, great cardiac vein and middle cardiac vein extend the atlas to 28 selectable groups. Official archive entries were fetched by HTTP range and verified against their ZIP central-directory CRC, with source SHA-256 records in the regenerated manifest. The GLB is unchanged on disk. At runtime, all atlas parts share an illustrative x/y/z scale of 0.86/1.12/0.94 before the camera transform, with inverse-scaled normals. This narrows and elongates the displayed assembly at the user's direction; it is not a dimensionally faithful anatomical measurement model. Selection, rendering and picking use the same transformed coordinates. The opening point cloud remains separate.
