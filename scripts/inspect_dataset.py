"""Preview a bounded CSV slice without assuming patients or a sampling rate."""
import argparse
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--path', type=Path, default=Path(__file__).resolve().parents[1] / 'app_and_ml/data/PPG_Dataset.csv')
    parser.add_argument('--row', type=int, default=0)
    parser.add_argument('--samples', type=int, default=1000)
    args = parser.parse_args()
    if args.row < 0 or not 1 <= args.samples <= 10000:
        parser.error('Use a nonnegative row and 1–10,000 samples.')
    frame = pd.read_csv(args.path, header=None, skiprows=args.row, nrows=1, usecols=range(args.samples))
    values = pd.to_numeric(frame.iloc[0], errors='coerce')
    fig = go.Figure(go.Scatter(y=values, line=dict(color='#00f2fe', width=2)))
    fig.update_layout(title=f'CSV row {args.row}: values as stored', xaxis_title='Sample index (timing unverified)',
                       yaxis_title='Stored value (units unverified)', template='plotly_dark')
    fig.show()


if __name__ == '__main__':
    main()
