import streamlit as st
import pandas as pd
import re
from io import StringIO, BytesIO


def format_file(file, filename):
    # Read uploaded file as text
    file_content = file.getvalue().decode("utf-8")
    lines = file_content.split("\n")

    column_names = ["Date", "Import ID", "Data", "Teaching Activity PID", "Field", "Value"]
    info_list = []

    for line in lines:
        datetime_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}):?')
        match = datetime_pattern.match(line)
        datetime_str = match.group(1) if match else ""

        # Extract bracketed and parenthesized contents
        bracket_pattern = re.compile(r'\[([^\]]*)\]')
        bracket_contents = bracket_pattern.findall(line)

        paren_pattern = re.compile(r'\(([^\)]+)\)')
        paren_contents = paren_pattern.findall(line)

        if len(bracket_contents) >= 4 and len(paren_contents) >= 2:
            info_line = [
                datetime_str,
                paren_contents[0],
                bracket_contents[0],
                paren_contents[1].split(',')[1],
                bracket_contents[2],
                bracket_contents[3]
            ]
            info_list.append(info_line)

    error_df = pd.DataFrame(info_list, columns=column_names)

    # Convert DataFrame to an in-memory Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        error_df.to_excel(writer, index=False)
    output.seek(0)

    # Generate a unique filename based on the uploaded file
    formatted_filename = filename.rsplit('.', 1)[0] + "_formatted.xlsx"

    return output, formatted_filename


# Streamlit UI
st.title("Log File Formatter")

uploaded_file = st.file_uploader("Upload a log file", type=["txt"])

if uploaded_file:
    st.success(f"File '{uploaded_file.name}' uploaded successfully!")

    # Process file and generate unique output filename
    formatted_file, output_filename = format_file(uploaded_file, uploaded_file.name)

    # Provide download button with the unique filename
    st.download_button(
        label=f"Download {output_filename}",
        data=formatted_file,
        file_name=output_filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
