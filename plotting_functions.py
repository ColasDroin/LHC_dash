#################### Imports ####################
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


#################### Functions ####################
def return_radial_background_traces(df_sv):
    # Add 4 radial lines, each parametrized with a different set of x1, x2, y1, y2
    l_traces_background = []
    for x1, x2, y1, y2 in [
        [np.mean(df_sv["X"]), np.mean(df_sv["X"]), -5000, 5000],
        [-10000, 1000, 0, 0],
        [-10000 + np.mean(df_sv["X"]), 10000 + np.mean(df_sv["X"]), -10000, 10000],
        [-10000 + np.mean(df_sv["X"]), 10000 + np.mean(df_sv["X"]), 10000, -10000],
    ]:
        l_traces_background.append(
            go.Scatter(
                x=[x1, x2],
                y=[y1, y2],
                mode="lines",
                name="Drift space",
                line_color="lightgrey",
                line_width=1,
                hoverinfo="skip",
                showlegend=False,
            )
        )

    # Return result in a list readable by plotly.add_traces()
    return l_traces_background


def return_beam_pipe_trace(df_sv):
    # Return a Plotly trace containing the beam pipe
    return go.Scatter(
        x=df_sv["X"],
        y=df_sv["Z"],
        mode="lines",
        name="Drift space",
        line_color="darkgrey",
        line_width=3,
        hoverinfo="skip",
        showlegend=False,
    )


def return_multipole_trace(
    df_elements,
    df_sv,
    order,
    strength_magnification_factor=5000,
    add_ghost_trace=True,
    l_indices_to_keep=None,
):
    # Get corresponding colors and name for the multipoles
    if order == 0:
        color = px.colors.qualitative.Plotly[0]
        name = "Dipoles"
    elif order == 1:
        color = px.colors.qualitative.Plotly[1]
        name = "Quadrupoles"
    elif order == 2:
        color = px.colors.qualitative.Plotly[-1]
        name = "Sextupoles"
    elif order == 3:
        color = px.colors.qualitative.Plotly[2]
        name = "Octupoles"

    # Get strength of all multipoles of the requested order
    s_knl = df_elements[df_elements.order == order]["knl"].apply(lambda x: x[order])

    # Remove zero-strength dipoles and magnify
    s_knl = s_knl[s_knl != 0] * strength_magnification_factor

    # Filter out indices outside of the range if needed
    if l_indices_to_keep is not None:
        s_knl = s_knl[s_knl.index.isin(l_indices_to_keep)]

    # Get corresponding lengths
    s_lengths = df_elements.loc[s_knl.index].length

    # Ghost trace for legend if requested
    if add_ghost_trace:
        ghost_trace = go.Scattergl(
            x=[10000, 10001],
            y=[0, 0],
            mode="lines",
            line=dict(color=color, width=5),
            showlegend=True,
            name=name,
            legendgroup=name,
        )

    # Add all multipoles individually (# ? Maybe one could use a scattergl with a list of x and y coordinates instead of a loop to gain time?)
    l_traces = []
    for i, row in df_sv.loc[s_knl.index].iterrows():
        theta = np.pi + row["theta"]

        # Correct for dipoles with zero height
        if abs(s_knl[i]) <= 0.5:
            s_knl[i] = np.sign(s_knl[i]) * 1.0

        # Add traces
        l_traces.append(
            go.Scattergl(
                x=[
                    # row["X"] - s_knl[i] / 2 * np.cos(theta),
                    row["X"],
                    # row["X"] + s_knl[i] / 2 * np.cos(theta),
                    row["X"] + s_knl[i] * np.cos(theta),
                ],
                y=[
                    row["Z"],
                    # row["Z"] + s_knl[i] / 2 * np.sin(theta),
                    row["Z"] + s_knl[i] * np.sin(theta),
                ],
                mode="lines",
                line=dict(
                    color=color,
                    width=np.ceil(s_lengths[i])
                    if not np.isnan(s_lengths[i]) or np.ceil(s_lengths[i]) == 0
                    else 1,
                ),
                showlegend=False,
                name=row["name"],
                legendgroup=name,
            )
        )

    # Return result in a list readable by plotly.add_traces()
    return [ghost_trace] + l_traces if add_ghost_trace else l_traces


def return_IP_trace(df_sv, add_ghost_trace=True):
    # Get dataframe containing only IP elements
    df_ip = df_sv[df_sv["name"].str.startswith("ip")]

    # Ghost trace for legend if requested
    if add_ghost_trace:
        ghost_trace = go.Scattergl(
            x=[10000, 10000],
            y=[0, 0],
            mode="markers",
            # marker_symbol=218,
            marker_line_color="midnightblue",
            marker_color="grey",
            marker_line_width=2,
            marker_size=15,
            showlegend=True,
            name="IP",
            legendgroup="IP",
        )

    # Add all IP individually
    l_traces = []
    for i, row in df_ip.iterrows():
        theta = np.pi + row["theta"]
        l_traces.append(
            go.Scattergl(
                mode="markers",
                x=[row["X"]],
                y=[row["Z"]],
                # marker_symbol="diamond",
                marker_line_color="midnightblue",
                marker_color="grey",
                marker_line_width=2,
                marker_size=15,
                name=row["name"],
                showlegend=False,
                legendgroup="IP",
            )
        )

    # Return result in a list readable by plotly.add_traces()
    return [ghost_trace] + l_traces if add_ghost_trace else l_traces


def return_optic_trace(df_sv, df_tw, type_trace, hide_optics_traces_initially=True, beam_2=False):
    # Get the right twiss dataframe and plotting parameters
    # ! Can't use match case as Python version on Swan is too old
    # match type_trace:
    #    case "betax":
    if type_trace == "betax":
        magnification_factor = 1.0
        tw_name = "betx"
        name = r"$\beta_{x2}^{0.8}$" if beam_2 else r"$\beta_{x1}^{0.8}$"
        color = px.colors.qualitative.Plotly[3]
        dash = "dash" if beam_2 else None
        exponent = 0.8

    # case "bety":
    elif type_trace == "bety":
        magnification_factor = 1.0
        tw_name = "bety"
        name = r"$\beta_{y2}^{0.8}$" if beam_2 else r"$\beta_{y1}^{0.8}$"
        color = px.colors.qualitative.Plotly[4]
        dash = "dash" if beam_2 else None
        exponent = 0.8

    # case "dx":
    elif type_trace == "dx":
        magnification_factor = 100
        tw_name = "dx"
        name = r"$100D_{x2}$" if beam_2 else r"$100D_{x1}$"
        color = px.colors.qualitative.Plotly[5]
        dash = "dash" if beam_2 else None
        exponent = 1.0

    # case "dy":
    elif type_trace == "dy":
        magnification_factor = 100
        tw_name = "dy"
        name = r"$100D_{y2}$" if beam_2 else r"$100D_{y1}$"
        color = px.colors.qualitative.Plotly[6]
        dash = "dash" if beam_2 else None
        exponent = 1.0

    # case "x":
    elif type_trace == "x":
        magnification_factor = 100000
        tw_name = "x"
        name = r"$10^5x2$" if beam_2 else r"$10^5x_1$"
        color = px.colors.qualitative.Plotly[7]
        dash = "dash" if beam_2 else None
        exponent = 1.0

    # case "y":
    elif type_trace == "y":
        magnification_factor = 100000
        tw_name = "y"
        name = r"$10^5y2$" if beam_2 else r"$10^5y_1$"
        color = px.colors.qualitative.Plotly[8]
        dash = "dash" if beam_2 else None
        exponent = 1.0

    # case _:
    else:
        print("The type of trace is not recognized.")

    # Correct for circular projection depending if x-coordinate has been reversed or not
    if beam_2:
        correction = -1
    else:
        correction = 1

    # Return the trace
    return go.Scattergl(
        x=df_sv["X"]
        - df_tw[tw_name] ** exponent * correction * magnification_factor * np.cos(df_sv["theta"]),
        y=df_sv["Z"] - df_tw[tw_name] ** exponent * magnification_factor * np.sin(df_sv["theta"]),
        mode="lines",
        line=dict(color=color, width=2, dash=dash),
        showlegend=True,
        name=name,
        visible="legendonly" if hide_optics_traces_initially else True,
    )


def add_multipoles_to_fig(
    fig,
    df_elements,
    df_sv,
    l_indices_to_keep,
    add_dipoles,
    add_quadrupoles,
    add_sextupoles,
    add_octupoles,
):
    # Add dipoles if requested
    if add_dipoles:
        fig.add_traces(
            return_multipole_trace(
                df_elements,
                df_sv,
                order=0,
                strength_magnification_factor=5000,
                l_indices_to_keep=l_indices_to_keep,
            )
        )

    # Add quadrupoles if requested
    if add_quadrupoles:
        fig.add_traces(
            return_multipole_trace(
                df_elements,
                df_sv,
                order=1,
                strength_magnification_factor=5000,
                l_indices_to_keep=l_indices_to_keep,
            )
        )

    # Add sextupoles if requested
    if add_sextupoles:
        fig.add_traces(
            return_multipole_trace(
                df_elements,
                df_sv,
                order=2,
                strength_magnification_factor=5000,
                l_indices_to_keep=l_indices_to_keep,
            )
        )

    # Add octupoles if requested
    if add_octupoles:
        fig.add_traces(
            return_multipole_trace(
                df_elements,
                df_sv,
                order=3,
                strength_magnification_factor=100,
                l_indices_to_keep=l_indices_to_keep,
            )
        )

    return fig


def add_optics_to_fig(
    fig,
    plot_horizontal_betatron,
    plot_vertical_betatron,
    plot_horizontal_dispersion,
    plot_vertical_dispersion,
    plot_horizontal_position,
    plot_vertical_position,
    df_sv,
    df_tw,
    beam_2=False,
):
    # Add horizontal betatron if requested
    if plot_horizontal_betatron:
        fig.add_trace(return_optic_trace(df_sv, df_tw, type_trace="betax", beam_2=beam_2))

    # Add vertical betatron if requested
    if plot_vertical_betatron:
        fig.add_trace(return_optic_trace(df_sv, df_tw, type_trace="bety", beam_2=beam_2))

    # Add horizontal dispersion if requested
    if plot_horizontal_dispersion:
        fig.add_trace(return_optic_trace(df_sv, df_tw, type_trace="dx", beam_2=beam_2))

    # Add vertical dispersion if requested
    if plot_vertical_dispersion:
        fig.add_trace(return_optic_trace(df_sv, df_tw, type_trace="dy", beam_2=beam_2))

    # Add horizontal position if requested
    if plot_horizontal_position:
        fig.add_trace(return_optic_trace(df_sv, df_tw, type_trace="x", beam_2=beam_2))

    # Add vertical position if requested
    if plot_vertical_position:
        fig.add_trace(return_optic_trace(df_sv, df_tw, type_trace="y", beam_2=beam_2))

    return fig


def return_plot_lattice_with_tracking(
    df_sv,
    df_elements,
    df_tw,
    df_sv_4=None,
    df_tw_4=None,
    add_dipoles=True,
    add_quadrupoles=True,
    add_sextupoles=True,
    add_octupoles=True,
    add_IP=True,
    l_indices_to_keep=None,
    plot_horizontal_betatron=True,
    plot_vertical_betatron=True,
    plot_horizontal_dispersion=True,
    plot_vertical_dispersion=True,
    plot_horizontal_position=True,
    plot_vertical_position=True,
    plot_horizontal_momentum=True,
    plot_vertical_momentum=True,
    hide_optics_traces_initially=True,
    add_optics_beam_2=True,
):
    # Center X coordinate (otherwise conversion to polar coordinates is not possible)
    X_centered = df_sv["X"] - np.mean(df_sv["X"])

    # Get corresponding angle
    l_theta = np.arctan2(df_sv["Z"], X_centered)

    # Build plotly figure
    fig = go.Figure()

    # Add lines to the bakckground delimit octants
    fig.add_traces(return_radial_background_traces(df_sv))

    # Add beam pipe
    fig.add_trace(return_beam_pipe_trace(df_sv))

    # Add multipoles
    fig = add_multipoles_to_fig(
        fig,
        df_elements,
        df_sv,
        l_indices_to_keep,
        add_dipoles,
        add_quadrupoles,
        add_sextupoles,
        add_octupoles,
    )

    # Add IP if requested
    if add_IP:
        fig.add_traces(return_IP_trace(df_sv))

    # Add optics traces for beam_1
    fig = add_optics_to_fig(
        fig,
        plot_horizontal_betatron,
        plot_vertical_betatron,
        plot_horizontal_dispersion,
        plot_vertical_dispersion,
        plot_horizontal_position,
        plot_vertical_position,
        df_sv,
        df_tw,
        beam_2=False,
    )

    # Add optics traces for beam_2 if requested
    if add_optics_beam_2:
        if df_sv_4 is None or df_tw_4 is None:
            print("Warning: df_sv_4 or df_tw_4 is None, beam_2 optics will not be plotted")
        else:
            fig = add_optics_to_fig(
                fig,
                plot_horizontal_betatron,
                plot_vertical_betatron,
                plot_horizontal_dispersion,
                plot_vertical_dispersion,
                plot_horizontal_position,
                plot_vertical_position,
                df_sv_4,
                df_tw_4,
                beam_2=True,
            )

    # Set general layout for figure
    fig.update_layout(
        title_text="LHC layout and beam dynamics",
        title_x=0.5,
        showlegend=True,
        xaxis_range=[df_sv["X"].min() - 300, df_sv["X"].max() + 300],
        yaxis_range=[df_sv["Z"].min() - 300, df_sv["Z"].max() + 300],
        xaxis_showgrid=True,
        xaxis_showticklabels=False,
        yaxis_showgrid=True,
        yaxis_scaleanchor="x",
        yaxis_scaleratio=1,
        yaxis_showticklabels=False,
        width=1000,
        height=1000,
        margin=dict(l=10, r=10, b=100, t=100, pad=10),
        dragmode="pan",
    )

    return fig
