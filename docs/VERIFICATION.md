# Testing and validation

## Automated checks

Run the Python suite with `python -m unittest discover -s tests -v` using the project's virtual environment. Run navigation checks with `node --test tests/test_navigation.cjs`. Platform-specific commands are in the README.

The Python suite covers:

- Generated waveforms, filtering, interpolation, derivatives and pulse-feature calculations.
- Generated video decoding, metadata handling, capture limits and stability selection.
- Missing measurements, irregular intervals and artifact rejection.
- Upload confirmation, short-recording consent, height conversion and retake state.
- All five Streamlit routes and licensed anatomy-asset integrity.

The JavaScript suite covers independent page scroll positions, navigation events and entrance behavior. Generated inputs verify known software behavior; they are not clinical reference recordings.

## Local recording checks

Three original smartphone MOV recordings were checked locally. Two passed the current software checks; one was withheld for inconsistent pulse timing. No independent clinical reference was available. The recordings and their waveform arrays are not distributed with the repository.

These checks do not establish physiological accuracy, sensitivity, specificity or compatibility with every phone and codec.

## Benchmark

The Architecture benchmark record is `app_and_ml/assets/architecture/benchmark.json`. It includes input parameters, raw timings, software versions and processing-source hashes.

It measures processing of an already-selected generated waveform. It excludes upload handling, video decoding, capture checks, stability selection, trimming and interface rendering. See [benchmark evidence](ARCHITECTURE_EVIDENCE.md).

## Platform scope

The application and interface were checked on macOS with Python 3.14. Windows and Linux installation instructions are provided, but those platforms have not been independently tested. Browser device emulation is not a substitute for testing on real phones.

## Clinical and anatomical limits

Recording-quality thresholds are engineering choices. They are not clinical confidence estimates, pressure measurements or a guarantee that every artifact has been detected. Independent reference comparisons and repeatability studies are still required.

The heart atlas is an educational illustration with adapted display proportions. It is not a clinical anatomical measurement tool.
