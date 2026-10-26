# Existing PPG dataset source

Source supplied by the team on October 26, 2026: [Photoplethysmography (PPG) Dataset on Kaggle](https://www.kaggle.com/datasets/ucimachinelearning/photoplethysmography-ppg-dataset).

The [publisher's public metadata endpoint](https://www.kaggle.com/api/v1/datasets/view/ucimachinelearning/photoplethysmography-ppg-dataset) was checked on the same date. It describes binary Normal / myocardial-infarction (MI) classification, lists CC BY-SA 4.0, and reports 63,798,840 bytes with an October 10, 2024 update. The source handle alone does not establish affiliation with the UCI repository, PhysioNet or MIMIC.

A bounded local inspection read the header and one data row from `app_and_ml/data/PPG_Dataset.csv`. The file is 63,798,840 bytes, consistent with the publisher's total. It has **2,001 columns: 2,000 indexed waveform values (`0` through `1999`) plus `Label`**. The first data row is labeled `MI`. File size and schema are consistent with the supplied source; a byte-for-byte comparison with a pinned download has not been performed. No waveform rows were changed or deleted, and the whole dataset was not scanned during this review.

**2,000 means waveform time points per row, not 2,000 patients.** The header contains no age, height, subject-ID or sampling-rate field. The source description reviewed does not specify a sampling frequency. We have not verified the number of rows, distinct patients, class counts, clinical adjudication or independence of train/test subjects.

## What the current site uses

- Telemetry analyzes the uploaded camera recording.
- Cohort Analytics uses 800 explicitly simulated observations for an age/timing-ratio illustration. That age relationship cannot be derived from this CSV, which has no age column.
- The Architecture speed benchmark uses a separate generated waveform. Its 1,000 input points are not cohort members or CSV records.
- The old training script ignored the CSV's classification label and derived a mock age target from waveform variance. That legacy model is not loaded by the current site.

## Appropriate next use

A dataset explorer could show actual waveform rows by their supplied Normal / MI labels, with sample index on the horizontal axis until sampling frequency is verified. Class counts should be calculated from the data rather than assumed. Any new model would need the correct binary target, documented preprocessing and a suitable held-out split; MI labels are not reference labels for arterial stiffness, vascular age or PAD risk tiers.

Patient-age trends, height-based SI, time-based heart-rate estimates and clinical accuracy claims need metadata or independent reference measurements that this header and source description do not supply. The source and license should accompany any adapted data display.
