---
paths:
  - "src/dashboard/**"
---

# Dashboard rules

- Design tokens are mirrored in `.streamlit/config.toml`, `theme.py` and `styles.py`.
  Change all three together. See "Theming" in the README.
- Target `data-testid`, `data-baseweb` and `st-key-*` in CSS. Never the hashed
  `.st-emotion-cache-*` names.
- Render Plotly figures with `theme=None`, or Streamlit replaces the figure's template.
- Pass every scraped value through `html.escape` in `components.py`.
- Filter, tab, search and page state live in `st.session_state`. Changing a filter resets
  the jobs table to page one.
- Data flows one way: `app.py` → `load_data.py` / `load_resources.py` / `load_defaults.py`
  → `pre_processing.py` → `sidebar.py` → `queries.py` → `plots.py` / `tables.py` →
  `components.py`. All dataframe filtering and aggregation belongs in `queries.py`.
- Develop without database credentials using `preview_with_snapshot.py`.
