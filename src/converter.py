import os
import re
import time
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from google import genai


# ========================================
# PROJECT PATH
# ========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = PROJECT_ROOT / "output"


# ========================================
# LOAD API KEY
# ========================================

load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is not found in .env"
    )


# ========================================
# GEMINI CLIENT
# ========================================

client = genai.Client(
    api_key=api_key
)


# ========================================
# GEMINI MODELS
# ========================================

MODELS = [
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
    "gemini-3.5-flash"
]

MAX_RETRIES_PER_MODEL = 2

MAX_CORRECTION_ATTEMPTS = 3


# ========================================
# GEMINI REQUEST WITH FALLBACK
# ========================================

def generate_with_fallback(prompt):

    last_error = None

    for model in MODELS:

        print("\n========================================")
        print(f"Trying Gemini model: {model}")
        print("========================================")

        for attempt in range(
            1,
            MAX_RETRIES_PER_MODEL + 1
        ):

            try:

                print(
                    f"Request attempt "
                    f"{attempt}/{MAX_RETRIES_PER_MODEL}"
                )

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                if not response.text:

                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                print(
                    f"Gemini response received "
                    f"from {model}"
                )

                return response.text, model

            except Exception as error:

                last_error = error

                error_text = str(error)

                print("\nGemini error:")
                print(error_text)

                temporary_error = (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "Service Unavailable" in error_text
                )

                if temporary_error:

                    if attempt < MAX_RETRIES_PER_MODEL:

                        wait_time = 2 ** attempt

                        print(
                            f"Retrying in "
                            f"{wait_time} seconds..."
                        )

                        time.sleep(wait_time)

                        continue

                    print(
                        f"{model} unavailable."
                    )

                    print(
                        "Trying next model..."
                    )

                    break

                if (
                    "404" in error_text
                    or "NOT_FOUND" in error_text
                ):

                    print(
                        f"{model} is not available."
                    )

                    print(
                        "Trying next model..."
                    )

                    break

                raise RuntimeError(
                    f"Gemini API error:\n"
                    f"{error_text}"
                ) from error

    raise RuntimeError(
        "All configured Gemini models are "
        "currently unavailable."
    ) from last_error


# ========================================
# READ FORTRAN
# ========================================

def read_fortran_file(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# ========================================
# CLEAN JAVA CODE
# ========================================

def clean_java_code(java_code):

    java_code = java_code.strip()

    java_code = re.sub(
        r"^```java\s*",
        "",
        java_code,
        flags=re.IGNORECASE
    )

    java_code = re.sub(
        r"^```\s*",
        "",
        java_code
    )

    java_code = re.sub(
        r"\s*```$",
        "",
        java_code
    )

    return java_code.strip()


# ========================================
# GET JAVA CLASS NAME
# ========================================

def get_java_class_name(java_code):

    match = re.search(
        r"public\s+class\s+([A-Za-z_][A-Za-z0-9_]*)",
        java_code
    )

    if match:
        return match.group(1)

    match = re.search(
        r"class\s+([A-Za-z_][A-Za-z0-9_]*)",
        java_code
    )

    if match:
        return match.group(1)

    raise ValueError(
        "Could not find Java class name."
    )


# ========================================
# CONVERT FORTRAN TO JAVA
# ========================================

def convert_fortran_to_java(
    fortran_code
):

    prompt = f"""
You are an expert software modernization
engineer specializing in legacy FORTRAN
to Java migration.

Convert the following FORTRAN program into
clean, equivalent Java code.

IMPORTANT REQUIREMENTS:

1. Preserve the original program logic.

2. Preserve variables and data types as
   closely as possible.

3. Convert FORTRAN arithmetic operations
   correctly.

4. Convert FORTRAN WRITE statements into
   appropriate Java output statements.

5. Convert FORTRAN READ statements into
   appropriate Java input handling.

6. Convert IF statements correctly.

7. Convert DO loops correctly.

8. Convert arrays correctly.

9. Preserve meaningful variable names.

10. Create a valid Java class.

11. The Java class must compile using javac.

12. Choose a meaningful Java class name
    based on the FORTRAN PROGRAM name.

13. Do not add unnecessary functionality.

14. Do not use external Java libraries.

15. Return ONLY Java source code.

16. Do NOT use Markdown code fences.

FORTRAN PROGRAM:

{fortran_code}
"""

    java_code, selected_model = (
        generate_with_fallback(prompt)
    )

    print(
        f"\nConversion model used: "
        f"{selected_model}"
    )

    return clean_java_code(
        java_code
    )


# ========================================
# COMPILE JAVA
# ========================================

def compile_java(
    java_file,
    class_name
):

    print("\nCompiling Java...")

    class_file = (
        OUTPUT_DIR /
        f"{class_name}.class"
    )

    if class_file.exists():
        class_file.unlink()

    result = subprocess.run(
        [
            "javac",
            str(java_file)
        ],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:

        print(
            "Java compilation: SUCCESS"
        )

        return True, ""

    print(
        "Java compilation: FAILED"
    )

    print("\nCompiler error:")
    print(result.stderr)

    return False, result.stderr


# ========================================
# AUTOMATIC JAVA CORRECTION
# ========================================

def correct_java_code(
    fortran_code,
    java_code,
    compiler_error,
    class_name
):

    print(
        "\nSending compiler error to Gemini..."
    )

    prompt = f"""
You are an expert Java debugging engineer
and legacy-code modernization engineer.

The Java code below was generated from
FORTRAN, but javac reported an error.

Fix the Java code.

IMPORTANT:

1. Preserve the original FORTRAN logic.

2. Fix the compiler error.

3. The Java code must compile using javac.

4. Keep the Java class name exactly:

{class_name}

5. Do not remove required functionality.

6. Return ONLY corrected Java source code.

7. Do NOT use Markdown code fences.

ORIGINAL FORTRAN:

{fortran_code}

CURRENT JAVA:

{java_code}

JAVAC ERROR:

{compiler_error}
"""

    corrected_code, selected_model = (
        generate_with_fallback(prompt)
    )

    print(
        f"Correction model used: "
        f"{selected_model}"
    )

    return clean_java_code(
        corrected_code
    )


# ========================================
# RUN JAVA
# ========================================

def run_java(
    class_name,
    timeout_seconds=10
):

    print(
        "\nRunning generated Java program..."
    )

    try:

        result = subprocess.run(
            [
                "java",
                "-cp",
                str(OUTPUT_DIR),
                class_name
            ],
            capture_output=True,
            text=True,
            timeout=timeout_seconds
        )

    except subprocess.TimeoutExpired:

        print(
            "Java execution timed out."
        )

        return None, (
            "Program execution timed out. "
            "The generated program may require "
            "user input."
        )

    if result.returncode == 0:

        output = result.stdout.strip()

        print(
            "Java execution: SUCCESS"
        )

        print("\nProgram output:")
        print(output)

        return output, ""

    print(
        "Java execution: FAILED"
    )

    print("\nRuntime error:")
    print(result.stderr)

    return None, result.stderr


# ========================================
# COMPLETE CONVERSION PIPELINE
# ========================================

def convert_file(
    input_file
):

    input_file = Path(input_file)

    if not input_file.exists():

        raise FileNotFoundError(
            f"FORTRAN file not found: "
            f"{input_file}"
        )

    print(
        "\n========================================"
    )

    print(
        "AI FORTRAN TO JAVA CODE CONVERTER"
    )

    print(
        "========================================"
    )

    print(
        f"\nInput file: {input_file}"
    )

    print(
        "\nReading FORTRAN file..."
    )

    fortran_code = read_fortran_file(
        input_file
    )

    print(
        "FORTRAN code loaded successfully."
    )

    # ========================================
    # GEMINI CONVERSION
    # ========================================

    print(
        "\nSending FORTRAN code to Gemini..."
    )

    java_code = convert_fortran_to_java(
        fortran_code
    )

    print(
        "\nGemini conversion completed."
    )

    # ========================================
    # FIND CLASS
    # ========================================

    class_name = get_java_class_name(
        java_code
    )

    print(
        "\nDetected Java class:"
    )

    print(class_name)

    # ========================================
    # OUTPUT DIRECTORY
    # ========================================

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    java_file = (
        OUTPUT_DIR /
        f"{class_name}.java"
    )

    # ========================================
    # SAVE JAVA
    # ========================================

    with open(
        java_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(java_code)

    print(
        "\nJava file created:"
    )

    print(java_file)

    # ========================================
    # COMPILE + CORRECTION LOOP
    # ========================================

    compilation_success = False

    compiler_error = ""

    for attempt in range(
        1,
        MAX_CORRECTION_ATTEMPTS + 1
    ):

        print(
            "\n----------------------------------------"
        )

        print(
            f"Validation attempt "
            f"{attempt}/"
            f"{MAX_CORRECTION_ATTEMPTS}"
        )

        print(
            "----------------------------------------"
        )

        (
            compilation_success,
            compiler_error
        ) = compile_java(
            java_file,
            class_name
        )

        if compilation_success:
            break

        if attempt < MAX_CORRECTION_ATTEMPTS:

            java_code = correct_java_code(
                fortran_code,
                java_code,
                compiler_error,
                class_name
            )

            with open(
                java_file,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(java_code)

            print(
                "\nCorrected Java code saved."
            )

    # ========================================
    # COMPILATION FAILURE
    # ========================================

    if not compilation_success:

        return {
            "success": False,
            "java_code": java_code,
            "java_file": java_file,
            "class_name": class_name,
            "execution_output": "",
            "error": compiler_error,
            "status": "Java compilation failed"
        }

    # ========================================
    # RUN JAVA
    # ========================================

    execution_output, runtime_error = (
        run_java(class_name)
    )

    # ========================================
    # FINAL RESULT
    # ========================================

    if runtime_error:

        return {
            "success": False,
            "java_code": java_code,
            "java_file": java_file,
            "class_name": class_name,
            "execution_output": "",
            "error": runtime_error,
            "status": "Java compilation succeeded, "
                      "but execution failed"
        }

    return {
        "success": True,
        "java_code": java_code,
        "java_file": java_file,
        "class_name": class_name,
        "execution_output": execution_output,
        "error": "",
        "status": "Conversion and validation successful"
    }


# ========================================
# COMMAND LINE TEST
# ========================================

def main():

    input_dir = PROJECT_ROOT / "input"

    fortran_files = []

    for extension in [
        "*.f90",
        "*.f",
        "*.for"
    ]:

        fortran_files.extend(
            input_dir.glob(extension)
        )

    if not fortran_files:

        print(
            "\nNo FORTRAN files found in:"
        )

        print(input_dir)

        return

    # Use the first FORTRAN file for
    # command-line testing.

    input_file = fortran_files[0]

    try:

        result = convert_file(
            input_file
        )

        print(
            "\n========================================"
        )

        print(
            result["status"]
        )

        print(
            "========================================"
        )

        if result["success"]:

            print(
                "\nExecution output:"
            )

            print(
                result["execution_output"]
            )

        else:

            print(
                "\nError:"
            )

            print(
                result["error"]
            )

    except Exception as error:

        print(
            "\n========================================"
        )

        print(
            "CONVERSION FAILED"
        )

        print(
            "========================================"
        )

        print(
            "\nError:"
        )

        print(error)


if __name__ == "__main__":
    main()
