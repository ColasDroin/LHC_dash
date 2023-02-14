#################### Imports ####################

# Import standard libraries
import dash_mantine_components as dmc
from dash import Dash, html, dcc, Input, Output, State, ctx
import dash
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
    title="LHC explorer",
)

#################### App Layout ####################
layout = html.Div(
    style={"width": "80%", "margin": "auto"},
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
                                dmc.Group(
                                    children=[
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
                                        dmc.Card(
                                            children=[
                                                dmc.Group(
                                                    [
                                                        dmc.Text(
                                                            id="title-element",
                                                            children="Element",
                                                            weight=500,
                                                        ),
                                                        dmc.Badge(
                                                            id="type-element",
                                                            children="Dipole",
                                                            color="blue",
                                                            variant="light",
                                                        ),
                                                    ],
                                                    position="apart",
                                                    mt="md",
                                                    mb="xs",
                                                ),
                                                html.Div(
                                                    id="text-element",
                                                    children=[
                                                        dmc.Text(
                                                            id="initial-text",
                                                            children=(
                                                                "Please click on a multipole or an"
                                                                " interaction point to get the"
                                                                " corresponding knob information."
                                                            ),
                                                            size="sm",
                                                            color="dimmed",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                            withBorder=True,
                                            shadow="sm",
                                            radius="md",
                                            style={"width": 350},
                                        ),
                                    ]
                                ),
                            ],
                        ),
                        dmc.Stack(
                            children=[
                                dmc.Center(
                                    dmc.Group(
                                        children=[
                                            dmc.Select(
                                                id="knob-select",
                                                data=list(tracker_b1.vars._owner.keys()),
                                                searchable=True,
                                                nothingFound="No options found",
                                                style={"width": 200},
                                                value="on_x1",
                                                label="Knob selection",
                                            ),
                                            dmc.NumberInput(
                                                id="knob-input",
                                                label="Knob value",
                                                value=tracker_b1.vars["on_x1"]._value,
                                                step=1,
                                                style={"width": 200},
                                            ),
                                            dmc.Button(
                                                "Update knob", id="update-knob-button", mr=10
                                            ),
                                            dmc.Button(
                                                "Display whole ring", id="display-ring-button"
                                            ),
                                            dmc.Button(
                                                "Display around IR 1", id="display-ir1-button"
                                            ),
                                            dmc.Button(
                                                "Display around IR 5", id="display-ir5-button"
                                            ),
                                        ],
                                        align="end",
                                    ),
                                ),
                                dmc.Group(
                                    children=[
                                        # dcc.Loading(
                                        # children=
                                        dcc.Graph(
                                            id="LHC-2D-near-IP",
                                            mathjax=True,
                                            config={
                                                "displayModeBar": True,
                                                "scrollZoom": True,
                                                "responsive": True,
                                                "displaylogo": False,
                                            },
                                        ),
                                        #    type="circle",
                                        # ),
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
    return tracker_b1.vars[value]._value


@app.callback(
    Output("LHC-2D-near-IP", "figure"),
    Output("LHC-2D-near-IP", "relayoutData"),
    Input("update-knob-button", "n_clicks"),
    Input("display-ring-button", "n_clicks"),
    Input("display-ir1-button", "n_clicks"),
    Input("display-ir5-button", "n_clicks"),
    State("knob-input", "value"),
    State("knob-select", "value"),
    State("LHC-2D-near-IP", "relayoutData"),
    State("LHC-2D-near-IP", "figure"),
    prevent_initial_call=False,
)
def update_graph_LHC_2D(
    n_click_knob, n_click_whole_ring, n_click_ir1, n_click_ir5, knob_value, knob, relayoutData, fig
):
    # Prevent problems if figure is not defined for any reason
    # if fig is None:
    #    return dash.no_update

    if ctx.triggered_id == "update-knob-button" or ctx.triggered_id is None:
        # Update knob if needed
        tracker_b1.vars[knob] = knob_value
        tw_b1 = tracker_b1.twiss()
        fig = plotting_functions.plot_around_IP(tw_b1)

        # Update figure ranges according to relayoutData
        if relayoutData is not None:
            fig["layout"]["xaxis"]["range"] = [
                relayoutData["xaxis.range[0]"],
                relayoutData["xaxis.range[1]"],
            ]
            fig["layout"]["xaxis2"]["range"] = [
                relayoutData["xaxis2.range[0]"],
                relayoutData["xaxis2.range[1]"],
            ]
            fig["layout"]["xaxis3"]["range"] = [
                relayoutData["xaxis3.range[0]"],
                relayoutData["xaxis3.range[1]"],
            ]
            fig["layout"]["xaxis"]["autorange"] = False

    else:
        # Update zoom level depending on button clicked
        match ctx.triggered_id:
            case "display-ring-button":
                x, y = [0, 26658.8832]
            case "display-ir1-button":
                x, y = [16247.725780457391, 23675.296424202796]
            case "display-ir5-button":
                x, y = [2833.530005905868, 10407.388328867295]
            case _:
                x, y = [0, 26658.8832]

        # Update figure ranges
        if "range" in fig["layout"]["xaxis"]:
            fig["layout"]["xaxis"]["range"] = [x, y]
            fig["layout"]["xaxis"]["autorange"] = False
        else:
            fig["layout"]["xaxis"] = {"range": [x, y], "autorange": False}

        if "range" in fig["layout"]["xaxis2"]:
            fig["layout"]["xaxis2"]["range"] = [x, y]
            fig["layout"]["xaxis2"]["autorange"] = False
        else:
            fig["layout"]["xaxis2"] = {"range": [x, y]}
            fig["layout"]["xaxis2"] = {"range": [x, y], "autorange": False}

        if "range" in fig["layout"]["xaxis3"]:
            fig["layout"]["xaxis3"]["range"] = [x, y]
            fig["layout"]["xaxis3"]["autorange"] = False
        else:
            fig["layout"]["xaxis3"] = {"range": [x, y]}
            fig["layout"]["xaxis3"] = {"range": [x, y], "autorange": False}

        # Update relayoutData as well
        if relayoutData is not None:
            relayoutData["xaxis.range[0]"] = x
            relayoutData["xaxis.range[1]"] = y
            relayoutData["xaxis2.range[0]"] = x
            relayoutData["xaxis2.range[1]"] = y
            relayoutData["xaxis3.range[0]"] = x
            relayoutData["xaxis3.range[1]"] = y
        else:
            relayoutData = {
                "xaxis.range[0]": x,
                "xaxis.range[1]": y,
                "xaxis2.range[0]": x,
                "xaxis2.range[1]": y,
                "xaxis3.range[0]": x,
                "xaxis3.range[1]": y,
            }

    return fig, relayoutData


@app.callback(
    Output("text-element", "children"),
    Output("title-element", "children"),
    Output("type-element", "children"),
    Input("LHC-layout", "clickData"),
    prevent_initial_call=False,
)
def update_text_graph_LHC_2D(clickData):
    if clickData is not None:
        if "customdata" in clickData["points"][0]:
            name = clickData["points"][0]["customdata"]
            if name.startswith("mb"):
                type_text = "Dipole"
                try:
                    set_var = tracker_b1.element_refs[name].knl[0]._expr._get_dependencies()
                except:
                    set_var = tracker_b1.element_refs[name + "..1"].knl[0]._expr._get_dependencies()
            elif name.startswith("mq"):
                type_text = "Quadrupole"
                try:
                    set_var = tracker_b1.element_refs[name].knl[1]._expr._get_dependencies()
                except:
                    set_var = tracker_b1.element_refs[name + "..1"].knl[1]._expr._get_dependencies()
            elif name.startswith("ms"):
                type_text = "Sextupole"
                try:
                    set_var = tracker_b1.element_refs[name].knl[2]._expr._get_dependencies()
                except:
                    set_var = tracker_b1.element_refs[name + "..1"].knl[2]._expr._get_dependencies()
            elif name.startswith("mo"):
                type_text = "Octupole"
                try:
                    set_var = tracker_b1.element_refs[name].knl[3]._expr._get_dependencies()
                except:
                    set_var = tracker_b1.element_refs[name + "..1"].knl[3]._expr._get_dependencies()

            text = []
            for var in set_var:
                name_var = str(var).split("'")[1]
                val = tracker_b1.vars[name_var]._get_value()
                expr = tracker_b1.vars[name_var]._expr
                if expr is not None:
                    dependencies = tracker_b1.vars[name_var]._expr._get_dependencies()
                else:
                    dependencies = "No dependencies"
                    expr = "No expression"
                targets = tracker_b1.vars[name_var]._find_dependant_targets()

                text.append(dmc.Text("Name: ", weight=500))
                text.append(dmc.Text(name_var, size="sm"))
                text.append(dmc.Text("Element value: ", weight=500))
                text.append(dmc.Text(str(val), size="sm"))
                text.append(dmc.Text("Expression: ", weight=500))
                text.append(dmc.Text(str(expr), size="sm"))
                text.append(dmc.Text("Dependencies: ", weight=500))
                text.append(dmc.Text(str(dependencies), size="sm"))
                text.append(dmc.Text("Targets: ", weight=500))
                if len(targets) > 10:
                    text.append(
                        dmc.Text(str(targets[:10]), size="sm"),
                    )
                    text.append(dmc.Text("...", size="sm"))
                else:
                    text.append(dmc.Text(str(targets), size="sm"))

            return text, name, type_text

    return dmc.Text(
        "Please click on a multipole to get the corresponding knob information.",
        "Click !", "Undefined type"
    )


#################### Launch app ####################
if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=8050)
