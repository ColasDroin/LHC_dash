#################### Imports ####################

# Import standard libraries
import dash_mantine_components as dmc
from dash import Dash, html, dcc, callback, Input, Output
import logging

# Import functions
from plotting_functions import return_plot_lattice_with_tracking
import loading_functions

#################### Get global variables ####################

# Get trackers and dataframes for beam 1 and 4
(
    line_b1,
    tracker_b1,
    df_elements_b1,
    df_sv_b1,
    df_tw_b1,
    df_elements_corrected_b1,
) = loading_functions.return_all_loaded_variables(
    "json_lines/line_b1.json", "temp/line_b1_dfs.pickle", force_load=False
)
(
    line_b4,
    tracker_b4,
    df_elements_b4,
    df_sv_b4,
    df_tw_b4,
    df_elements_corrected_b4,
) = loading_functions.return_all_loaded_variables(
    "json_lines/line_b4.json", "temp/line_b4_dfs.pickle", force_load=False
)


#################### App ####################
app = Dash(
    __name__,
    external_scripts=[
        "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML"
    ],
)

#################### App Layout ####################
layout = html.Div(
    children=[
        dmc.Header(
            height=50,
            children=dmc.Center(
                style={"height": "100%", "width": "100%"},
                children=dmc.Text("LHC explorer", size=30),
            ),
        ),
        html.Div(
            id="main-div",
            children=[
                dcc.Graph(id="LHC_layout", mathjax=True, config={"displayModeBar": False}),
            ],
        ),
    ]
)
app.layout = layout


#################### App Callbacks ####################
@app.callback(
    Output("LHC_layout", "figure"),
    Input("main-div", "style"),
)
def update_graph(xstyle):
    # Get indices of elements to keep (# ! implemented only for beam 1)
    l_indices_to_keep = loading_functions.get_indices_of_interest(df_tw_b1, "ip4", "ip6")

    fig = return_plot_lattice_with_tracking(
        df_sv_b1,
        df_elements_corrected_b1,
        df_tw_b1,
        df_sv_4=df_sv_b4,
        df_tw_4=df_tw_b4,
        l_indices_to_keep=l_indices_to_keep,
    )

    return fig


#################### Launch app ####################
if __name__ == "__main__":
    app.run_server(debug=False)
