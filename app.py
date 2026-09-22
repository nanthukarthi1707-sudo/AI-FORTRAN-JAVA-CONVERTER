import sys
from pathlib import Path

import streamlit as st


# ========================================
# PROJECT PATH
# ========================================

PROJECT_ROOT = Path(__file__).resolve().parent

INPUT_DIR = PROJECT_ROOT / "input"

OUTPUT_DIR = PROJECT_ROOT / "output"

SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(
    0,
    str(SRC_DIR)
)

from converter import convert_file


# ========================================
# PAGE CONFIG
# ========================================

st.set_page_config(
    page_title="AI FORTRAN to Java Converter",
    page_icon="🤖",
    layout="wide"
)


# ========================================
# HEADER
# ========================================

st.title(
    "🤖 AI-Powered FORTRAN to Java Converter"
)

st.subheader(
    "Legacy Code Modernization using Gemini AI"
)

st.write(
    "Convert legacy FORTRAN programs into "
    "modern Java code with AI-powered "
    "conversion, compilation and validation."
)

st.divider()


# ========================================
# SIDEBAR
# ========================================

with st.sidebar:

    st.header(
        "⚙️ Project Information"
    )

    st.write(
        "**AI:** Gemini Flash"
    )

    st.write(
        "**Source:** FORTRAN"
    )

    st.write(
        "**Target:** Java"
    )

    st.write(
        "**Compiler:** javac"
    )

    st.write(
        "**Framework:** Streamlit"
    )

    st.divider()

    st.info(
        "Upload a FORTRAN source file "
        "and convert it into Java."
    )


# ========================================
# FILE UPLOAD
# ========================================

st.header(
    "📂 Upload FORTRAN Program"
)

uploaded_file = st.file_uploader(
    "Choose a FORTRAN source file",
    type=[
        "f90",
        "f",
        "for"
    ]
)


# ========================================
# WHEN FILE IS UPLOADED
# ========================================

if uploaded_file is not None:

    st.success(
        f"File selected: "
        f"{uploaded_file.name}"
    )

    try:

        fortran_code = (
            uploaded_file
            .read()
            .decode("utf-8")
        )

    except UnicodeDecodeError:

        st.error(
            "Unable to read this file as UTF-8."
        )

        st.stop()

    # ========================================
    # SHOW FORTRAN
    # ========================================

    st.subheader(
        "📄 FORTRAN Source Code"
    )

    st.code(
        fortran_code,
        language="fortran"
    )

    st.divider()

    # ========================================
    # CONVERT BUTTON
    # ========================================

    if st.button(
        "🚀 Convert to Java",
        type="primary",
        use_container_width=True
    ):

        # ====================================
        # SAVE UPLOADED FILE
        # ====================================

        INPUT_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        safe_filename = Path(
            uploaded_file.name
        ).name

        input_file = (
            INPUT_DIR /
            safe_filename
        )

        with open(
            input_file,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(fortran_code)

        # ====================================
        # START CONVERSION
        # ====================================

        st.info(
            "🔄 Sending FORTRAN code to Gemini..."
        )

        try:

            result = convert_file(
                input_file
            )

            # ====================================
            # RESULT STATUS
            # ====================================

            if result["success"]:

                st.success(
                    "🎉 Conversion and validation "
                    "completed successfully!"
                )

            else:

                st.error(
                    result["status"]
                )

            # ====================================
            # GENERATED JAVA
            # ====================================

            st.subheader(
                "☕ Generated Java Code"
            )

            st.code(
                result["java_code"],
                language="java"
            )

            # ====================================
            # JAVA FILE
            # ====================================

            java_file = result["java_file"]

            st.success(
                f"Java file: "
                f"{java_file.name}"
            )

            # ====================================
            # DOWNLOAD
            # ====================================

            st.download_button(
                label="⬇️ Download Java File",
                data=result["java_code"],
                file_name=java_file.name,
                mime="text/x-java-source",
                use_container_width=True
            )

            # ====================================
            # EXECUTION OUTPUT
            # ====================================

            if result["execution_output"]:

                st.subheader(
                    "▶️ Java Program Output"
                )

                st.code(
                    result["execution_output"],
                    language="text"
                )

            # ====================================
            # ERROR
            # ====================================

            if result["error"]:

                with st.expander(
                    "🔍 Error Details"
                ):

                    st.code(
                        result["error"],
                        language="text"
                    )

        except Exception as error:

            st.error(
                "❌ Conversion failed."
            )

            with st.expander(
                "🔍 Error Details"
            ):

                st.code(
                    str(error),
                    language="text"
                )


# ========================================
# NO FILE
# ========================================

else:

    st.info(
        "👆 Upload a FORTRAN .f90, .f or .for "
        "file to begin."
    )


# ========================================
# FOOTER
# ========================================

st.divider()

st.caption(
    "AI-Powered Legacy FORTRAN to Java "
    "Code Converter | "
    "Python + Gemini + Java + Streamlit"
)