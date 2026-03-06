import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load data
df = pd.read_csv("global_placement.csv")

app = dash.Dash(__name__)

# ---------------- Layout ----------------

app.layout = html.Div([

    html.H1(
        "🎓 Global Student Placement Dashboard",
        style={"textAlign":"center","color":"white","marginBottom":"30px"}
    ),

    # Filters
    html.Div([

        dcc.Dropdown(
            id="country_filter",
            options=[{"label":i,"value":i} for i in sorted(df["country"].unique())],
            placeholder="Select Country",
            multi=True
        ),

        dcc.Dropdown(
            id="tier_filter",
            options=[{"label":i,"value":i} for i in sorted(df["college_tier"].unique())],
            placeholder="Select College Tier",
            multi=True
        ),

        dcc.Dropdown(
            id="spec_filter",
            options=[{"label":i,"value":i} for i in sorted(df["specialization"].unique())],
            placeholder="Select Specialization",
            multi=True
        ),

    ], style={
        "display":"grid",
        "gridTemplateColumns":"1fr 1fr 1fr",
        "gap":"20px",
        "marginBottom":"30px"
    }),

    # KPI Cards
    html.Div([
        html.Div(id="total_students",className="card"),
        html.Div(id="placed_students",className="card"),
        html.Div(id="placement_rate",className="card"),
        html.Div(id="avg_salary",className="card")
    ], style={
        "display":"grid",
        "gridTemplateColumns":"repeat(4,1fr)",
        "gap":"20px",
        "marginBottom":"30px"
    }),

    # Row 1
    html.Div([
        dcc.Graph(id="tier_chart"),
        dcc.Graph(id="salary_chart")
    ], style={
        "display":"grid",
        "gridTemplateColumns":"1fr 1fr",
        "gap":"20px"
    }),

    # Row 2
    html.Div([
        dcc.Graph(id="cgpa_chart"),
        dcc.Graph(id="country_chart")
    ], style={
        "display":"grid",
        "gridTemplateColumns":"1fr 1fr",
        "gap":"20px"
    }),

    # Row 3
    html.Div([
        dcc.Graph(id="industry_chart"),
        dcc.Graph(id="heatmap_chart")
    ], style={
        "display":"grid",
        "gridTemplateColumns":"1fr 1fr",
        "gap":"20px"
    })

], style={
    "backgroundColor":"#0f172a",
    "padding":"30px",
    "fontFamily":"Arial"
})

# ---------------- Callback ----------------

@app.callback(

[
Output("total_students","children"),
Output("placed_students","children"),
Output("placement_rate","children"),
Output("avg_salary","children"),
Output("tier_chart","figure"),
Output("salary_chart","figure"),
Output("cgpa_chart","figure"),
Output("country_chart","figure"),
Output("industry_chart","figure"),
Output("heatmap_chart","figure"),
],

[
Input("country_filter","value"),
Input("tier_filter","value"),
Input("spec_filter","value")
]

)

def update_dashboard(country,tier,spec):

    dff = df.copy()

    if country:
        dff = dff[dff["country"].isin(country)]

    if tier:
        dff = dff[dff["college_tier"].isin(tier)]

    if spec:
        dff = dff[dff["specialization"].isin(spec)]

    # KPI
    total = len(dff)
    placed = (dff["placement_status"]=="Placed").sum()
    rate = round((placed/total)*100,2) if total>0 else 0
    salary = round(dff["salary"].mean(),2)

    card_style = {
        "background":"linear-gradient(135deg,#2563eb,#1e3a8a)",
        "padding":"20px",
        "borderRadius":"10px",
        "color":"white",
        "textAlign":"center",
        "boxShadow":"0 4px 10px rgba(0,0,0,0.4)"
    }

    card1 = html.Div([html.H4("Total Students"),html.H2(total)],style=card_style)
    card2 = html.Div([html.H4("Placed Students"),html.H2(placed)],style=card_style)
    card3 = html.Div([html.H4("Placement Rate"),html.H2(f"{rate}%")],style=card_style)
    card4 = html.Div([html.H4("Avg Salary"),html.H2(salary)],style=card_style)

    # Charts

    tier_rate = (
        dff.groupby("college_tier")["placement_status"]
        .value_counts(normalize=True)
        .unstack()["Placed"]*100
    ).reset_index()

    fig_tier = px.bar(
        tier_rate,
        x="college_tier",
        y="Placed",
        title="Placement Rate by College Tier",
        template="plotly_dark"
    )

    fig_salary = px.histogram(
        dff,
        x="salary",
        title="Salary Distribution",
        template="plotly_dark"
    )

    fig_cgpa = px.scatter(
        dff,
        x="cgpa",
        y="salary",
        color="placement_status",
        title="CGPA vs Salary",
        template="plotly_dark"
    )

    country_place = (
        dff[dff["placement_status"]=="Placed"]
        .groupby("country")
        .size()
        .reset_index(name="count")
    )

    fig_country = px.bar(
        country_place,
        x="country",
        y="count",
        title="Placement Count by Country",
        template="plotly_dark"
    )

    industry = (
        dff[dff["placement_status"]=="Placed"]
        .groupby("industry")
        .size()
        .reset_index(name="count")
    )

    fig_industry = px.bar(
        industry,
        x="industry",
        y="count",
        title="Industry Hiring Distribution",
        template="plotly_dark"
    )

    corr = dff.corr(numeric_only=True)

    fig_heatmap = px.imshow(
        corr,
        text_auto=True,
        title="Correlation Heatmap",
        template="plotly_dark"
    )

    return card1,card2,card3,card4,fig_tier,fig_salary,fig_cgpa,fig_country,fig_industry,fig_heatmap


# Run app
if __name__ == "__main__":
    app.run(debug=True)