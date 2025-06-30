import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
from pathlib import Path

st.set_page_config(page_title="Voting Tracker", layout="wide")
st.title("Графа с OnlyScreens (30.06.2025)")
st.badge("Сделано эстонским гандоном.")
# -- Settings --
UPLOADS_DIR = "gamejam"
def parse_voting_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Extract snapshot timestamp from the last non-empty line
    last_line = ""
    for line in reversed(text.splitlines()):
        if line.strip():
            last_line = line.strip()
            break
    if last_line.startswith("📅"):
        full_label = last_line.replace("📅", "").replace("Последнее обновление:", "").strip()
        # full_label looks like "30.06.2025 10:19"
        # Trim to only time part
        snapshot_label = full_label.split()[-1]  # take last part after space, e.g. "10:19"
    else:
        snapshot_label = file_path.stem

    projects = []
    pattern = r"Проект: (.*?)\n💫 Баллы: (\d+)\n⭐️ Средний балл: ([\d\.]+)"
    matches = re.findall(pattern, text)
    for match in matches:
        name, points, avg = match
        projects.append({
            'project': name.strip(),
            'points': int(points),
            'average': float(avg),
            'snapshot': snapshot_label
        })
    return projects



# -- Load all snapshots --
all_files = sorted(Path(UPLOADS_DIR).glob("*.txt"), key=lambda x: x.stem)
data = []

for file in all_files:
    data.extend(parse_voting_file(file))

df = pd.DataFrame(data)

if df.empty:
    st.warning(f"Данных не было найдено, все ли в порядке?")
    st.stop()

# -- UI to select project --
project_list = sorted(df['project'].unique())
project = st.selectbox("Выберите проект", project_list)

project_df = df[df['project'] == project].sort_values('snapshot')

# -- Plot --
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=project_df['snapshot'],
    y=project_df['points'],
    mode='lines+markers',
    name='Очки',
    line=dict(color='royalblue', width=2),
    hovertemplate='%{y}'
))
fig.add_trace(go.Scatter(
    x=project_df['snapshot'],
    y=project_df['average'],
    mode='lines+markers',
    name='Средний балл',
    line=dict(color='orange', width=2),
    hovertemplate='%{y}'
))

fig.update_layout(
    title=f"Голосование для: {project}",
    xaxis_title="Время",
    yaxis_title="Очки",
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    hovermode='x unified',
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# -- Data display --
with st.expander("Показать 'сырые' данные"):
    st.dataframe(project_df, use_container_width=True)
