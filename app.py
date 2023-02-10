#################### Imports ####################

# Import standard libraries
import dash_mantine_components as dmc
from dash import Dash, html, dcc, Input, Output, State
import logging

# Import functions
import plotting_functions
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
    "json_lines/line_b1.json", "temp/line_b1_dfs.pickle", force_load=False, correct_x_axis=True
)
(
    line_b4,
    tracker_b4,
    df_elements_b4,
    df_sv_b4,
    df_tw_b4,
    df_elements_corrected_b4,
) = loading_functions.return_all_loaded_variables(
    "json_lines/line_b4.json", "temp/line_b4_dfs.pickle", force_load=False, correct_x_axis=False
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
    style={"width": "80%"},
    children=[
        dmc.Header(
            height=50,
            children=dmc.Center(
                children=dmc.Text("LHC explorer", size=30),
            ),
            style={"margin": "auto"},
        ),
        dmc.Center(
            children=[
                html.Div(
                    id="main-div",
                    children=[
                        dmc.Stack(
                            children=[
                                dmc.Center(
                                    children=[
                                        dmc.Group(
                                            children=[
                                                dmc.Text("Sectors to display: "),
                                                dmc.ChipGroup(
                                                    [
                                                        dmc.Chip(
                                                            x,
                                                            value=x,
                                                            variant="outline",
                                                        )
                                                        for x in ["8-2", "2-4", "4-6", "6-8"]
                                                    ],
                                                    id="chips-ip",
                                                    value=["4-6"],
                                                    multiple=True,
                                                    mb=10,
                                                ),
                                            ],
                                            pt=10,
                                        ),
                                    ],
                                ),
                                dcc.Loading(
                                    children=dcc.Graph(
                                        id="LHC-layout",
                                        mathjax=True,
                                        config={
                                            "displayModeBar": True,
                                            "scrollZoom": True,
                                            "responsive": True,
                                            "displaylogo": False,
                                        },
                                    ),
                                    type="circle",
                                ),
                            ],
                        ),
                        dmc.Stack(
                            children=[
                                dmc.Group(
                                    children=[
                                        dmc.Select(
                                            id="knob-select",
                                            data=list(tracker_b1.vars._owner.keys()),
                                            searchable=True,
                                            nothingFound="No options found",
                                            style={"width": 200},
                                            value="on_x1",
                                        ),
                                        dmc.NumberInput(
                                            id="knob-input",
                                            label="Knob value",
                                            value=tracker_b1.vars["on_x1"]._value,
                                            step=1,
                                            style={"width": 200},
                                        ),
                                    ],
                                ),
                                dmc.Group(
                                    children=[
                                        dcc.Loading(
                                            children=dcc.Graph(
                                                id="LHC-2D-near-IP",
                                                mathjax=True,
                                                config={
                                                    "displayModeBar": True,
                                                    "scrollZoom": True,
                                                    "responsive": True,
                                                    "displaylogo": False,
                                                },
                                            ),
                                            type="circle",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)
app.layout = layout


#################### App Callbacks ####################
@app.callback(
    Output("LHC-layout", "figure"),
    Input("chips-ip", "value"),
)
def update_graph_LHC_layout(l_values):
    l_indices_to_keep = []
    for val in l_values:
        str_ind_1, str_ind_2 = val.split("-")
        # Get indices of elements to keep (# ! implemented only for beam 1)
        l_indices_to_keep.extend(
            loading_functions.get_indices_of_interest(df_tw_b1, "ip" + str_ind_1, "ip" + str_ind_2)
        )

    fig = plotting_functions.return_plot_lattice_with_tracking(
        df_sv_b1,
        df_elements_corrected_b1,
        df_tw_b1,
        df_sv_4=df_sv_b4,
        df_tw_4=df_tw_b4,
        l_indices_to_keep=l_indices_to_keep,
    )

    return fig


@app.callback(
    Output("knob-input", "value"),
    Input("knob-select", "value"),
)
def update_knob_input(value):
    return tracker_b1.vars[value]


@app.callback(
    Output("LHC-2D_near-IP", "figure"),
    Input("knob-input", "value"),
    State("knob-select", "value"),
)
def update_graph_LHC_2D_near_IP(value, knob):
    # Initialize crossing angle at 0
    tracker_b1.vars[knob] = value
    tw_b1 = tracker_b1.twiss()
    twmb19r5 = tw_b1.get_twiss_init(at_element="mb.b19l5.b1")
    tw_part = tracker_b1.twiss(ele_start="mb.b19l5.b1", ele_stop="mb.b19r5.b1", twiss_init=twmb19r5)

    fig = plotting_functions.plot_around_IP(tw_part)

    return fig


#################### Launch app ####################
if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=8050)
