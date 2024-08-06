import re

import numpy as np
import pandas as pd

from .utility import (
    apply_restriction_on_c_df,
    apply_restriction_on_df,
    city_country_mapped_list,
    contains_bom_or_missing_price,
    convert_str_to_dict,
    convert_to_usd,
    get_end_of_table,
    get_header,
    get_mapping,
    get_mapping_data,
    get_response,
    get_rest_data_map,
    has_valid_header,
    update_city_country,
    update_city_value,
    update_country_value,
    update_row,
    update_unit_cost
)


def process_format_a(uploaded_file):
    df = pd.read_excel(uploaded_file, sheet_name=0)
    df = df.fillna("")

    # Step 1: Identify the row from the excel which is having the column header
    header, header_index = get_header(df)

    # Step 2: Identify the end of table
    end_table_row_index = get_end_of_table(df, header_index)

    # Step 3: Identify rest of the page data
    header_row = df.iloc[header_index]
    before_header = df.iloc[:header_index]
    after_end_row = df.iloc[end_table_row_index + 1 :]

    # Step 4: Map the rows as per destination from both table headers and rest of the data in 2 step.
    rest_data_df = pd.concat(
        [before_header, after_end_row, header_row], ignore_index=True
    )
    rest_data_df = rest_data_df.fillna("")
    desired_columns = [
        "Date",
        "Item",
        "Description",
        "Country",
        "City",
        "Supplier",
        "Quote #",
        "Currency",
        "Total Cost",
        "QTY",
        "Hours",
        "Unit Cost",
        "Unit Cost (USD)",
    ]

    mapped_dict = get_mapping(
        header, desired_columns, df.iloc[header_index + 2].to_string(index=False)
    )
    mapped_dict = convert_str_to_dict(mapped_dict)
    rest_data = get_rest_data_map(rest_data_df.to_csv(), desired_columns)
    rest_data = convert_str_to_dict(rest_data)

    # Step 5: Generate the destination table data
    df_destination = df.iloc[header_index:end_table_row_index]
    df_destination.columns = df_destination.iloc[0]
    df_destination = df_destination[1:]
    df_destination.reset_index(drop=True, inplace=True)

    # Create a new DataFrame with columns based on the mapped dictionary
    new_columns = {v: k for k, v in mapped_dict.items() if v in df_destination.columns}
    new_df = df_destination[list(new_columns.keys())].rename(columns=new_columns)
    # remove duplicate
    new_df = new_df.loc[:, ~new_df.columns.duplicated()]

    # Add empty columns for the remaining mappings
    for new_col in mapped_dict.keys():
        if new_col and new_col not in new_df.columns:
            new_df[new_col] = ""

    # Fill the remaining columns with the rest of the data
    for col, value in rest_data.items():
        if col in new_df.columns and value:
            new_df[col] = value

    new_df = apply_restriction_on_df(new_df)
    city_to_country, country_list = city_country_mapped_list()
    new_df = new_df.apply(
        update_city_country,
        axis=1,
        city_to_country=city_to_country,
        country_list=country_list,
    )
    new_df = update_unit_cost(new_df)
    new_df["Unit Cost (USD)"] = new_df.apply(
        lambda row: convert_to_usd(row["Unit Cost"], row["Currency"]), axis=1
    )
    return new_df


def process_format_b(uploaded_file):
    sheets = pd.read_excel(uploaded_file, sheet_name=None)
    df_str = ""
    for sheet in sheets:
        is_match = re.search(
            "terms|condition|sow|assumption|change|bom", sheet, re.IGNORECASE
        )
        if not is_match:
            df = pd.DataFrame(sheets[sheet])
            df = df.fillna("")
            df = df.dropna()
            df = df.replace({"^x$": "0"}, regex=True)

            df_str += df.to_string(header=False, index=False)

    df_str = re.sub("\n", "\n\n", df_str)
    df_str = re.sub("\n[\s]+\n", "", df_str)

    desired_columns = [
        "Date",
        "Item",
        "Description",
        "Country",
        "City",
        "Supplier",
        "Quote #",
        "Currency",
        "Total Cost",
        "QTY",
        "Hours",
        "Unit Cost",
        "Unit Cost (USD)",
    ]
    response = get_response(df_str, desired_columns)
    response = response.drop(response[response["Total Cost"] == 0].index).reset_index()

    return response


def process_format_c(uploaded_file):
    sheet_data = {}
    quotation_sheet_data = {}
    excel_file = pd.ExcelFile(uploaded_file)
    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
        df = df.fillna("")
        is_header = False

        # Step 1: Identify the row from the excel which is having the column header
        if has_valid_header(df):
            header = df.columns.tolist()
            header_index = 0
            is_header = True
        else:
            header, header_index = get_header(df)

        # check for the quotation sheet
        if "quotation" in sheet_name.lower():
            quotation_sheet_data[sheet_name] = {
                "header": header,
                "header_index": header_index,
                "df": df,
                "is_header": is_header,
            }

        # Step 2: Check BOM present in header if yes then do not use that sheet
        if contains_bom_or_missing_price(header):
            continue

        sheet_data[sheet_name] = {
            "header": header,
            "header_index": header_index,
            "df": df,
            "is_header": is_header,
        }

    # Step 3: Map the header with desired columns
    desired_columns = [
        "Date",
        "Item",
        "Description",
        "Country",
        "City",
        "Supplier",
        "Quote #",
        "Currency",
        "Total Cost",
        "QTY",
        "Hours",
        "Unit Cost",
        "Unit Cost (USD)",
    ]
    for key, value in sheet_data.items():
        df = value["df"]
        header = value["header"]
        header_index = value["header_index"]

        mapped_dict = get_mapping_data(
            header, desired_columns, df.iloc[header_index + 2].to_string(index=False)
        )
        mapped_dict = convert_str_to_dict(mapped_dict)
        sheet_data[key]["mapped_dict"] = mapped_dict

    # Work on quotation Sheet Data:
    keys = quotation_sheet_data.keys()
    if len(keys) > 0:
        key = list(keys)[0]
        is_header = quotation_sheet_data[key]["is_header"]
        df = quotation_sheet_data[key]["df"]
        df = df.dropna()
        header_index = quotation_sheet_data[key]["header_index"]
        if not is_header:
            quotation_df = df.iloc[header_index:]
            quotation_df.columns = quotation_df.iloc[0]
            quotation_df = quotation_df[1:]
            quotation_df.reset_index(drop=True, inplace=True)
        else:
            quotation_df = df

    df_list = []
    for key, value in sheet_data.items():
        is_header = value["is_header"]
        df = value["df"]
        df = df.dropna()
        header_index = value["header_index"]
        mapped_dict = value["mapped_dict"]

        # Step 5: Generate the destination table data
        if not is_header:
            df_destination = df.iloc[header_index:]
            df_destination.columns = df_destination.iloc[0]
            df_destination = df_destination[1:]
            df_destination.reset_index(drop=True, inplace=True)
        else:
            df_destination = df

        # for mapping the data with other sheet, initial prep
        df_destination.replace("", np.nan, inplace=True)
        df_destination.columns = ["Match Key"] + list(df_destination.columns[1:])
        df_destination["Match Key"] = df_destination["Match Key"].ffill()
        df_destination = df_destination.fillna("")

        # Create a new DataFrame with columns based on the mapped dictionary
        new_columns = {
            v: k for k, v in mapped_dict.items() if v in df_destination.columns
        }
        new_columns["Match Key"] = "Match Key"
        new_df = df_destination[list(new_columns.keys())].rename(columns=new_columns)
        # remove duplicate
        new_df = new_df.loc[:, ~new_df.columns.duplicated()]

        # Add empty columns for the remaining mappings
        for new_col in mapped_dict.keys():
            if new_col and new_col not in new_df.columns:
                new_df[new_col] = ""

        # Add the rest data from quotation sheet
        new_df = new_df.apply(lambda row: update_row(row, quotation_df), axis=1)

        new_df = apply_restriction_on_c_df(new_df)
        new_df = update_unit_cost(new_df)
        new_df["Currency"] = "USD"
        new_df["Unit Cost (USD)"] = new_df.apply(
            lambda row: convert_to_usd(row["Unit Cost"], row["Currency"]), axis=1
        )
        df_list.append(new_df)

    # combine the dataframes
    combined_df = pd.concat(df_list, ignore_index=True)
    combined_df["City"] = combined_df["City"].apply(update_city_value)
    combined_df["Country"] = combined_df["Country"].apply(update_country_value)
    combined_df = combined_df.drop("Match Key", axis=1)

    return combined_df
