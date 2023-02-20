#################### Imports ####################
import numpy as np
import json
import pandas as pd
import xtrack as xt
import pickle
import os

#################### Functions ####################


def return_line_from_file(file_path):
    """Return the line from a json file."""
    # Load the line
    with open(file_path, "r") as fid:
        dct = json.load(fid)
        line = xt.Line.from_dict(dct)

    return line


def return_dataframe_elements_from_line(line):
    # Build a dataframe with the elements of the lines
    df_elements = pd.DataFrame([x.to_dict() for x in line.elements])
    return df_elements


def return_survey_and_twiss_dataframes_from_tracker(tracker, correct_x_axis=True):
    """Return the survey and twiss dataframes from a tracker."""
    # Get survey dataframes
    df_sv = tracker.survey().to_pandas()

    # Get Twiss dataframes
    tw = tracker.twiss()
    df_tw = tw.to_pandas()

    # Reverse x-axis if requested
    if correct_x_axis:
        df_sv["X"] = -df_sv["X"]
        df_tw["x"] = -df_tw["x"]

    return df_sv, df_tw


def return_dataframe_corrected_for_thin_lens_approx(df_elements, df_tw):
    """Correct the dataframe of elements for thin lens approximation."""
    df_elements_corrected = df_elements.copy(deep=True)

    # Add all thin lenses (length + strength)
    for i, row in df_tw.iterrows():
        # Correct for thin lens approximation and weird duplicates
        if ".." in row["name"] and "f" not in row["name"].split("..")[1]:
            name = row["name"].split("..")[0]
            index = df_tw[df_tw.name == name].index[0]

            # Add length
            if np.isnan(df_elements_corrected.loc[index]["length"]):
                df_elements_corrected.at[index, "length"] = 0.0
            df_elements_corrected.at[index, "length"] += df_elements.loc[i]["length"]

            # Add strength
            if np.isnan(df_elements_corrected.loc[index]["knl"]).all():
                df_elements_corrected.at[index, "knl"] = (
                    np.array([0.0] * df_elements.loc[i]["knl"].shape[0], dtype=np.float64)
                    if type(df_elements.loc[i]["knl"]) != float
                    else 0.0
                )
            df_elements_corrected.at[index, "knl"] = (
                df_elements_corrected.loc[index, "knl"] + np.array(df_elements.loc[i]["knl"])
                if type(df_elements.loc[i]["knl"]) != float
                else df_elements.loc[i]["knl"]
            )

            # Replace order
            df_elements_corrected.at[index, "order"] = df_elements.loc[i]["order"]

            # Drop row
            df_elements_corrected.drop(i, inplace=True)

    return df_elements_corrected


def return_all_loaded_variables(
    save_path=None, force_load=False, correct_x_axis=True, line_path=None, line=None
):
    """Return all loaded variables if they are not already loaded."""

    if line is None and line_path is not None:
        # Rebuild line (can't be pickled, most likely because of struct and multiprocessing)
        line = return_line_from_file(line_path)

    elif line is None and line_path is None:
        raise ValueError("Either line or line_path must be provided")

    # Build tracker
    tracker = line.build_tracker()

    # Check if df are already saved
    if save_path is not None and os.path.exists(save_path):
        with open(save_path, "rb") as handle:
            df_elements, df_sv, df_tw, df_elements_corrected = pickle.load(handle)
    else:
        df_elements = return_dataframe_elements_from_line(line)
        df_sv, df_tw = return_survey_and_twiss_dataframes_from_tracker(tracker, correct_x_axis)
        df_elements_corrected = return_dataframe_corrected_for_thin_lens_approx(df_elements, df_tw)

    if save_path is not None:
        # Save variables
        with open(save_path, "wb") as handle:
            pickle.dump([df_elements, df_sv, df_tw, df_elements_corrected], handle)

    # Return all variables
    return line, tracker, df_elements, df_sv, df_tw, df_elements_corrected


def get_indices_of_interest(df_tw, element_1, element_2):
    """Return the indices of the elements of interest."""
    idx_1 = df_tw.loc[df_tw["name"] == element_1].index[0]
    idx_2 = df_tw.loc[df_tw["name"] == element_2].index[0]
    if idx_2 < idx_1:
        return list(range(0, idx_2)) + list(range(idx_1, len(df_tw)))
    return list(range(idx_1, idx_2))
