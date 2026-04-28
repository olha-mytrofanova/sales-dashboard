import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import pandas as pd

df = pd.read_csv("data.csv")
df["date"] = pd.to_datetime(df["date"])

app = dash.Dash(__name__)

card_style = {
    "background": "white",
    "padding": "20px 24px",
    "borderRadius": "8px",
    "flex": "1",
    "boxShadow": "0 2px 6px rgba(0,0,0,0.1)",
    "fontFamily": "Arial"
}

app.layout = html.Div([

    html.H1("Sales & Marketing Dashboard",
            style={"fontFamily": "Arial", "color": "#2c3e50", "padding": "20px 40px 0"}),

    html.Div([
        html.Div([
            html.P("Category", style={"margin": "0 0 6px", "color": "#7f8c8d", "fontSize": "13px"}),
            dcc.Dropdown(
                id="category-filter",
                options=[{"label": c, "value": c} for c in sorted(df["category"].unique())],
                multi=True,
                placeholder="All categories",
            )
        ], style={"flex": "1"}),
        html.Div([
            html.P("Region", style={"margin": "0 0 6px", "color": "#7f8c8d", "fontSize": "13px"}),
            dcc.Dropdown(
                id="region-filter",
                options=[{"label": r, "value": r} for r in sorted(df["region"].unique())],
                multi=True,
                placeholder="All regions",
            )
        ], style={"flex": "1"}),
    ], style={"display": "flex", "gap": "20px", "padding": "16px 40px"}),

    html.Div([
        html.Div([
            html.P("Total Revenue", style={"margin": "0 0 4px", "color": "#7f8c8d", "fontSize": "13px"}),
            html.H3(id="total-revenue", style={"margin": "0", "color": "#2c3e50", "fontSize": "28px"})
        ], style=card_style),
        html.Div([
            html.P("Total Units Sold", style={"margin": "0 0 4px", "color": "#7f8c8d", "fontSize": "13px"}),
            html.H3(id="total-units", style={"margin": "0", "color": "#2c3e50", "fontSize": "28px"})
        ], style=card_style),
        html.Div([
            html.P("Overall ROAS", style={"margin": "0 0 4px", "color": "#7f8c8d", "fontSize": "13px"}),
            html.H3(id="total-roas", style={"margin": "0", "color": "#27ae60", "fontSize": "28px"})
        ], style=card_style),
        html.Div([
            html.P("Total Ad Spend", style={"margin": "0 0 4px", "color": "#7f8c8d", "fontSize": "13px"}),
            html.H3(id="total-spend", style={"margin": "0", "color": "#e74c3c", "fontSize": "28px"})
        ], style=card_style),
    ], style={"display": "flex", "gap": "20px", "padding": "0 40px 20px"}),

    html.Div([
        dcc.Graph(id="revenue-by-region"),
        dcc.Graph(id="revenue-trend"),
    ], style={"display": "flex", "gap": "20px", "padding": "0 40px"}),

    html.Div([
        dcc.Graph(id="category-breakdown"),
        dcc.Graph(id="scatter-plot"),
    ], style={"display": "flex", "gap": "20px", "padding": "20px 40px"}),

    html.H3("Top Performers by Region & Category",
            style={"fontFamily": "Arial", "color": "#2c3e50", "padding": "0 40px"}),

    html.Div(id="table-container", style={"padding": "0 40px 40px"}),

], style={"background": "#f5f5f5", "minHeight": "100vh"})


@app.callback(
    Output("total-revenue", "children"),
    Output("total-units", "children"),
    Output("total-roas", "children"),
    Output("total-spend", "children"),
    Output("revenue-by-region", "figure"),
    Output("revenue-trend", "figure"),
    Output("category-breakdown", "figure"),
    Output("scatter-plot", "figure"),
    Output("table-container", "children"),
    Input("category-filter", "value"),
    Input("region-filter", "value")
)
def update(selected_cat, selected_reg):
    filtered = df.copy()
    if selected_cat:
        filtered = filtered[filtered["category"].isin(selected_cat)]
    if selected_reg:
        filtered = filtered[filtered["region"].isin(selected_reg)]

    total_rev = f"${filtered['revenue'].sum():,}"
    total_units = f"{filtered['units_sold'].sum():,}"
    total_spend = f"${filtered['ad_spend'].sum():,}"
    roas = round(filtered['revenue'].sum() / filtered['ad_spend'].sum(), 2)

    fig1 = px.bar(
        filtered.groupby("region")["revenue"].sum().reset_index(),
        x="region", y="revenue", title="Revenue by Region",
        color="region", color_discrete_sequence=px.colors.qualitative.Set2
    )

    monthly = filtered.groupby(filtered["date"].dt.to_period("M"))["revenue"].sum().reset_index()
    monthly["date"] = monthly["date"].astype(str)
    fig2 = px.line(monthly, x="date", y="revenue", title="Revenue Trend", markers=True)
    fig2.update_traces(line_color="#3498db")

    fig3 = px.bar(
        filtered.groupby("category")[["revenue", "ad_spend"]].sum().reset_index(),
        x="category", y=["revenue", "ad_spend"],
        title="Revenue vs Ad Spend by Category", barmode="group",
        color_discrete_sequence=["#2ecc71", "#e74c3c"]
    )

    fig4 = px.scatter(
        filtered, x="ad_spend", y="revenue",
        color="category", size="units_sold",
        title="Ad Spend vs Revenue (bubble size = units sold)",
        trendline="ols",
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    for fig in [fig1, fig2, fig3, fig4]:
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")

    table_df = filtered.groupby(["region", "category"]).agg(
        revenue=("revenue", "sum"),
        units_sold=("units_sold", "sum"),
        ad_spend=("ad_spend", "sum")
    ).reset_index().sort_values("revenue", ascending=False).head(10)
    table_df["roas"] = (table_df["revenue"] / table_df["ad_spend"]).round(2)
    table_df["revenue"] = table_df["revenue"].apply(lambda x: f"${x:,}")
    table_df["ad_spend"] = table_df["ad_spend"].apply(lambda x: f"${x:,}")

    table = dash_table.DataTable(
        data=table_df.to_dict("records"),
        columns=[{"name": c.replace("_", " ").title(), "id": c} for c in table_df.columns],
        style_table={"borderRadius": "8px", "overflow": "hidden"},
        style_header={"backgroundColor": "#2c3e50", "color": "white", "fontWeight": "bold", "fontFamily": "Arial"},
        style_cell={"fontFamily": "Arial", "padding": "10px", "textAlign": "left"},
        style_data_conditional=[{"if": {"row_index": "odd"}, "backgroundColor": "#f8f9fa"}]
    )

    return total_rev, total_units, f"{roas}x", total_spend, fig1, fig2, fig3, fig4, table


if __name__ == "__main__":
    app.run(debug=True)