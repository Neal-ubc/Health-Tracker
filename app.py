import json
import os
from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Override with the DATA_DIR environment variable to point at storage that
# survives redeploys (e.g. "/home/data" on Azure Web App — everything under
# /home persists across restarts, but a git-based deploy replaces the repo's
# own working directory each time, which would wipe a relative "data" path).
DATA_DIR = os.environ.get("DATA_DIR", "data")
BASELINE_PATH = os.path.join(DATA_DIR, "baseline.json")
ENTRIES_PATH = os.path.join(DATA_DIR, "entries.csv")

INK = "#1B3A5C"
PAPER = "#EAF1F8"
PANEL = "#F5F9FD"
AMBER = "#C1873C"
TEAL = "#3F7C6E"
ROSE = "#B25454"
BLUE = "#4A7FB5"
MUTE = "#5B7086"

st.set_page_config(page_title="Health ledger", page_icon="📒", layout="centered")


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_baseline():
    ensure_data_dir()
    if os.path.exists(BASELINE_PATH):
        with open(BASELINE_PATH, "r") as f:
            return json.load(f)
    return {"weight": None, "height": None, "age": None, "date": str(date.today())}


def save_baseline(baseline):
    ensure_data_dir()
    with open(BASELINE_PATH, "w") as f:
        json.dump(baseline, f)


def load_entries():
    ensure_data_dir()
    if os.path.exists(ENTRIES_PATH):
        df = pd.read_csv(ENTRIES_PATH)
        if "exercises" not in df.columns:
            df["exercises"] = "[]"
        return df
    return pd.DataFrame(columns=["date", "calories", "weight", "exercises"])


def save_entries(df):
    ensure_data_dir()
    df.to_csv(ENTRIES_PATH, index=False)


def calc_bmi(weight_kg, height_cm):
    if not weight_kg or not height_cm:
        return None
    h = height_cm / 100
    return weight_kg / (h * h)


def bmi_category(bmi):
    if bmi is None:
        return "—", MUTE
    if bmi < 18.5:
        return "underweight", BLUE
    if bmi < 25:
        return "healthy range", TEAL
    if bmi < 30:
        return "overweight", AMBER
    return "obese", ROSE


def bmi_gauge(bmi):
    label, color = bmi_category(bmi)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=bmi if bmi is not None else 0,
            number={"suffix": "", "font": {"color": INK, "size": 32}},
            gauge={
                "axis": {"range": [15, 40], "tickcolor": MUTE, "tickfont": {"color": MUTE, "size": 10}},
                "bar": {"color": INK, "thickness": 0.25},
                "bgcolor": PANEL,
                "borderwidth": 0,
                "steps": [
                    {"range": [15, 18.5], "color": BLUE},
                    {"range": [18.5, 25], "color": TEAL},
                    {"range": [25, 30], "color": AMBER},
                    {"range": [30, 40], "color": ROSE},
                ],
            },
        )
    )
    fig.update_layout(
        height=220,
        margin=dict(l=20, r=20, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "IBM Plex Mono, monospace"},
    )
    return fig, label, color


def inject_style():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');
        .stApp {{ background-color: {PAPER}; }}
        h1, h2, h3 {{ font-family: 'Fraunces', serif !important; color: {INK} !important; }}
        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; color: {INK}; }}
        .ledger-note {{ color: {MUTE}; font-size: 0.85rem; }}
        div[data-testid="stMetricValue"] {{ font-family: 'IBM Plex Mono', monospace; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    inject_style()
    st.title("Health ledger")
    st.markdown(
        f"<p class='ledger-note'>A running record of intake, effort, and weight. Today is {date.today().isoformat()}.</p>",
        unsafe_allow_html=True,
    )

    baseline = st.session_state.get("baseline", load_baseline())
    entries = st.session_state.get("entries", load_entries())
    st.session_state["baseline"] = baseline
    st.session_state["entries"] = entries

    tab_today, tab_baseline, tab_history = st.tabs(["Log today", "Baseline", "History"])

    with tab_baseline:
        st.subheader("Your baseline")
        col1, col2 = st.columns([1, 1])
        with col1:
            weight = st.number_input(
                "Weight (kg)", min_value=0.0, step=0.1,
                value=float(baseline["weight"]) if baseline.get("weight") else 0.0,
            )
            height = st.number_input(
                "Height (cm)", min_value=0.0, step=0.5,
                value=float(baseline["height"]) if baseline.get("height") else 0.0,
            )
            age = st.number_input(
                "Age", min_value=0, step=1,
                value=int(baseline["age"]) if baseline.get("age") else 0,
            )
            recorded_on = st.date_input(
                "Recorded on",
                value=date.fromisoformat(baseline["date"]) if baseline.get("date") else date.today(),
            )
            if st.button("Save baseline"):
                new_baseline = {
                    "weight": weight or None,
                    "height": height or None,
                    "age": age or None,
                    "date": str(recorded_on),
                }
                save_baseline(new_baseline)
                st.session_state["baseline"] = new_baseline
                st.success("Baseline saved.")
                st.rerun()
        with col2:
            bmi = calc_bmi(weight, height)
            fig, label, color = bmi_gauge(bmi)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(
                f"<p style='text-align:center;color:{color};font-weight:500;'>{label}</p>",
                unsafe_allow_html=True,
            )

    with tab_today:
        st.subheader("Log an entry")

        if "draft_exercises" not in st.session_state:
            st.session_state["draft_exercises"] = []

        c1, c2, c3 = st.columns(3)
        with c1:
            log_date = st.date_input("Date", value=date.today(), key="log_date")
        with c2:
            log_calories = st.number_input("Calorie intake", min_value=0, step=10, key="log_calories")
        with c3:
            log_weight = st.number_input("Weight today (kg)", min_value=0.0, step=0.1, key="log_weight")

        st.markdown("**Activities**")
        if st.session_state["draft_exercises"]:
            for i, ex in enumerate(st.session_state["draft_exercises"]):
                ecol1, ecol2, ecol3 = st.columns([3, 2, 1])
                ecol1.write(ex["name"])
                ecol2.write(f"{ex.get('minutes', '')} min · {ex.get('calories', '')} kcal")
                if ecol3.button("Remove", key=f"remove_{i}"):
                    st.session_state["draft_exercises"].pop(i)
                    st.rerun()

        with st.form("add_activity", clear_on_submit=True):
            ac1, ac2, ac3 = st.columns([3, 1, 1])
            ex_name = ac1.text_input("Activity name", placeholder="Running")
            ex_minutes = ac2.number_input("Minutes", min_value=0, step=5)
            ex_calories = ac3.number_input("Calories burned", min_value=0, step=10)
            if st.form_submit_button("Add activity") and ex_name.strip():
                st.session_state["draft_exercises"].append(
                    {"name": ex_name.strip(), "minutes": ex_minutes, "calories": ex_calories}
                )
                st.rerun()

        entry_exists = str(log_date) in st.session_state["entries"]["date"].astype(str).values
        confirm_overwrite = True
        if entry_exists:
            st.warning(f"An entry for {log_date} already exists. Saving will overwrite it.")
            confirm_overwrite = st.checkbox(
                f"Overwrite existing entry for {log_date}",
                key=f"confirm_overwrite_{log_date}",
            )

        if st.button("Save entry", type="primary", disabled=entry_exists and not confirm_overwrite):
            df = st.session_state["entries"]
            df = df[df["date"] != str(log_date)]
            new_row = pd.DataFrame(
                [{
                    "date": str(log_date),
                    "calories": log_calories,
                    "weight": log_weight,
                    "exercises": json.dumps(st.session_state["draft_exercises"]),
                }]
            )
            df = pd.concat([df, new_row], ignore_index=True)
            save_entries(df)
            st.session_state["entries"] = df
            st.session_state["draft_exercises"] = []
            st.success(f"Saved entry for {log_date}")
            st.rerun()

    with tab_history:
        df = st.session_state["entries"]
        if df.empty:
            st.info("Nothing logged yet. Add your first entry from the Log today tab.")
        else:
            df_sorted = df.sort_values("date")
            st.subheader("Weight and intake over time")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_sorted["date"], y=df_sorted["weight"], name="Weight (kg)",
                mode="lines+markers", line=dict(color=TEAL, width=2), yaxis="y1",
            ))
            fig.add_trace(go.Scatter(
                x=df_sorted["date"], y=df_sorted["calories"], name="Calories",
                mode="lines+markers", line=dict(color=AMBER, width=2), yaxis="y2",
            ))
            fig.update_layout(
                height=320,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(title="Weight (kg)", side="left"),
                yaxis2=dict(title="Calories", side="right", overlaying="y"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                font={"family": "Inter, sans-serif", "color": INK},
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Entries")
            for _, row in df_sorted.sort_values("date", ascending=False).iterrows():
                exercises = json.loads(row["exercises"]) if pd.notna(row["exercises"]) else []
                burned = sum(float(x.get("calories", 0) or 0) for x in exercises)
                names = ", ".join(x["name"] for x in exercises)
                with st.container(border=True):
                    ec1, ec2 = st.columns([4, 1])
                    pending_key = f"confirm_delete_{row['date']}"
                    if st.session_state.get(pending_key):
                        ec1.markdown(f"**{row['date']}** — delete this entry?")
                        dcol1, dcol2 = ec2.columns(2)
                        if dcol1.button("Yes", key=f"confirm_{row['date']}"):
                            df = df[df["date"] != row["date"]]
                            save_entries(df)
                            st.session_state["entries"] = df
                            st.session_state.pop(pending_key, None)
                            st.rerun()
                        if dcol2.button("No", key=f"cancel_{row['date']}"):
                            st.session_state.pop(pending_key, None)
                            st.rerun()
                    else:
                        ec1.markdown(f"**{row['date']}**")
                        if ec2.button("Delete", key=f"del_{row['date']}"):
                            st.session_state[pending_key] = True
                            st.rerun()
                    parts = []
                    if pd.notna(row["calories"]):
                        parts.append(f"intake **{row['calories']} kcal**")
                    if pd.notna(row["weight"]):
                        parts.append(f"weight **{row['weight']} kg**")
                    if burned:
                        parts.append(f"burned **{burned:.0f} kcal**")
                    if names:
                        parts.append(f"activities **{names}**")
                    st.markdown(" · ".join(parts) if parts else "—")


if __name__ == "__main__":
    main()
