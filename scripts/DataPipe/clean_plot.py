import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path


def plot_sauna_temp(
    df,
    temp_col,
    model,
    serial_number,
    test_date,
    interval=5,
    marker_size=14,
    show_time=False,
    dot_color='#F05A40',
    line_color='#4F67FF'
):
    """
    Sauna temperature plot.

    Required:
        elapsed_Mins, CP_timer, temp_F/temp_C

    Optional:
        time (only required when show_time=True)

    Custom colors:
        dot_color  = marker color
        line_color = temperature line color
    """

    # Validate
    required = ['elapsed_Mins', 'CP_timer', temp_col]

    if show_time:
        required.append('time')

    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # Unit
    unit = '°F' if temp_col == 'temp_F' else '°C' if temp_col == 'temp_C' else '°'

    # Clean
    df = df.copy()
    df['elapsed_Mins'] = pd.to_numeric(df['elapsed_Mins'], errors='coerce')
    df = df.dropna(subset=['elapsed_Mins', temp_col])
    df = df.sort_values('elapsed_Mins').reset_index(drop=True)

    # Uniform interval positions
    max_elapsed = df['elapsed_Mins'].max()
    tick_positions = np.arange(0, max_elapsed + interval, interval)

    # Nearest actual measurement to each interval
    rows = []

    for x in tick_positions:
        idx = (df['elapsed_Mins'] - x).abs().idxmin()
        row = df.loc[idx].copy()
        row['plot_x'] = x
        rows.append(row)

    df_plot = pd.DataFrame(rows)

    # Theme
    navy = '#203A5F'
    plot_bg = '#E7EDF6'
    band = '#F1F5FA'
    grid = '#FFFFFF'
    gray = '#4B5563'

    fig = go.Figure()

    # Temperature line
    fig.add_trace(go.Scatter(
        x=df['elapsed_Mins'],
        y=df[temp_col],
        mode='lines',
        line=dict(width=3, color=line_color, shape='spline'),
        hovertemplate=(
            '<b>Elapsed:</b> %{x:.1f} min<br>'
            f'<b>Temperature:</b> %{{y:.1f}}{unit}'
            '<extra></extra>'
        ),
        showlegend=False
    ))

    # Hover data
    hover_cols = ['time', 'CP_timer', 'elapsed_Mins'] if show_time else ['CP_timer', 'elapsed_Mins']

    if show_time:
        hover_template = (
            '<b>Time:</b> %{customdata[0]}<br>'
            '<b>Elapsed:</b> %{customdata[2]:.1f} min<br>'
            '<b>CP Timer:</b> %{customdata[1]:.0f}<br>'
            f'<b>Temperature:</b> %{{y:.1f}}{unit}'
            '<extra></extra>'
        )
    else:
        hover_template = (
            '<b>Elapsed:</b> %{customdata[1]:.1f} min<br>'
            '<b>CP Timer:</b> %{customdata[0]:.0f}<br>'
            f'<b>Temperature:</b> %{{y:.1f}}{unit}'
            '<extra></extra>'
        )

    # Markers + labels
    fig.add_trace(go.Scatter(
        x=df_plot['plot_x'],
        y=df_plot[temp_col],
        mode='markers+text',
        marker=dict(
            size=marker_size,
            color=dot_color,
            line=dict(width=1.5, color='white')
        ),
        text='<b>' + df_plot[temp_col].round().astype(int).astype(str) + f'{unit}</b>',
        textposition='top center',
        textfont=dict(size=15, color=navy),
        customdata=df_plot[hover_cols],
        hovertemplate=hover_template,
        showlegend=False
    ))

    # X-axis
    fig.update_xaxes(
        tickmode='array',
        tickvals=tick_positions,
        showticklabels=False,
        ticks='',
        showline=True,
        linewidth=1.5,
        linecolor=navy,
        showgrid=True,
        gridcolor=grid,
        gridwidth=1,
        zeroline=False,
        range=[-interval * 0.4, tick_positions[-1] + interval * 0.4]
    )

    # Y-axis
    fig.update_yaxes(
        title=dict(
            text=f'<b>Temperature ({unit})</b>',
            font=dict(size=18, color=navy)
        ),
        tickfont=dict(size=13, color=navy),
        ticks='outside',
        ticklen=5,
        tickcolor=navy,
        showline=True,
        linewidth=1.5,
        linecolor=navy,
        showgrid=True,
        gridcolor=grid,
        gridwidth=1,
        zeroline=False
    )

    # Bottom band
    bottom = -0.20 if show_time else -0.13

    fig.add_shape(
        type='rect',
        x0=0, x1=1,
        y0=bottom, y1=0,
        xref='paper', yref='paper',
        fillcolor=band,
        line=dict(width=0),
        layer='below'
    )

    # Label positions
    elapsed_y = -0.045
    timer_y = -0.095
    time_y = -0.155

    # Bottom values
    for _, row in df_plot.iterrows():

        fig.add_annotation(
            x=row['plot_x'], y=elapsed_y,
            xref='x', yref='paper',
            text=f"<b>{int(row['plot_x'])}</b>",
            showarrow=False,
            xanchor='center',
            yanchor='middle',
            font=dict(size=13, color=navy)
        )

        fig.add_annotation(
            x=row['plot_x'], y=timer_y,
            xref='x', yref='paper',
            text=f"<b>{row['CP_timer']:.0f}</b>",
            showarrow=False,
            xanchor='center',
            yanchor='middle',
            font=dict(size=13, color=navy)
        )

        if show_time:
            fig.add_annotation(
                x=row['plot_x'], y=time_y,
                xref='x', yref='paper',
                text=str(row['time']),
                showarrow=False,
                xanchor='center',
                yanchor='middle',
                font=dict(size=12, color=gray)
            )

    # Right-side labels
    labels = [
        (elapsed_y, 'Elapsed'),
        (timer_y, 'CP Timer')
    ]

    if show_time:
        labels.append((time_y, 'Time'))

    for y, label in labels:
        fig.add_annotation(
            x=1.015, y=y,
            xref='paper', yref='paper',
            text=f'<b>{label}</b>',
            showarrow=False,
            xanchor='left',
            yanchor='middle',
            font=dict(size=13, color=navy)
        )

    # Separator
    fig.add_shape(
        type='line',
        x0=0, x1=1,
        y0=-0.07, y1=-0.07,
        xref='paper', yref='paper',
        line=dict(color='#D9E1EC', width=1)
    )

    # Header accent
    fig.add_shape(
        type='line',
        x0=0, x1=1,
        y0=1.04, y1=1.04,
        xref='paper', yref='paper',
        line=dict(color=line_color, width=3)
    )

    # Layout
    fig.update_layout(
        title=dict(
            text=f'<b>{model} - SN {serial_number} | Date {test_date}</b>',
            x=0.5,
            xanchor='center',
            y=0.97,
            font=dict(size=22, color=navy)
        ),
        font=dict(family='Arial', size=14, color=navy),
        height=700,
        paper_bgcolor='white',
        plot_bgcolor=plot_bg,
        margin=dict(l=120, r=150, t=110, b=155 if show_time else 120),
        hovermode='closest',
        hoverlabel=dict(
            bgcolor='white',
            bordercolor='#D5DDEA',
            font=dict(size=13, color=navy)
        ),
        showlegend=False
    )



    return fig


def main(csv_path: str | Path | None = None) -> None:
    """Plot a cleaned CSV written as time, elapsed_Mins, CP_timer, temp_C, temp_F."""
    import os
    from datetime import datetime

    if csv_path is None:
        import argparse
        parser = argparse.ArgumentParser(description='Plot a cleaned sauna CSV.')
        parser.add_argument('csv', type=Path)
        csv_path = parser.parse_args().csv

    csv_path = Path(csv_path)
    frame = pd.read_csv(csv_path)
    test_date = datetime.strptime(csv_path.name.split('_', 1)[0], '%Y-%m-%d').strftime('%m/%d/%Y')
    model = os.getenv('TEST_UNIT', csv_path.stem)
    serial_number = os.getenv('SERIAL_NUMBER', '')
    charts = (
        ('temp_F', 'F'),
        ('temp_C', 'C'),
    )
    for temp_col, suffix in charts:
        figure = plot_sauna_temp(
            frame,
            temp_col=temp_col,
            model=model,
            serial_number=serial_number,
            test_date=test_date,
        )
        png_path = csv_path.with_name(f'{csv_path.name.removesuffix("_clean.csv")}_{suffix}.png')
        figure.write_image(str(png_path))
        print(f'Chart saved to: {png_path}')


if __name__ == '__main__':
    main()