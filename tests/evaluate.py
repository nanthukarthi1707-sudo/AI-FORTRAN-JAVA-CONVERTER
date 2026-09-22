from pathlib import Path
import sys

# Add project src folder to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

from converter import convert_file


TEST_FILES = [
    "calculator.f90",
    "sum.f90",
    "if_test.f90",
    "loop_test.f90",
    "array_test.f90",
]


def main():
    input_dir = PROJECT_ROOT / "input"

    total = len(TEST_FILES)
    successful = 0
    api_failures = 0
    compilation_failures = 0
    execution_failures = 0
    test_errors = 0

    print("=" * 60)
    print("AI FORTRAN TO JAVA - EVALUATION")
    print("=" * 60)

    for test_file in TEST_FILES:
        input_file = input_dir / test_file

        print("\n" + "-" * 60)
        print(f"Testing: {test_file}")
        print("-" * 60)

        try:
            result = convert_file(input_file)

            if result["success"]:
                successful += 1

                print("RESULT: SUCCESS")
                print(f"Java class: {result['class_name']}")
                print(f"Output: {result['execution_output']}")

            else:
                error = result["error"]
                status = result["status"]

                error_lower = error.lower()

                # Gemini API / quota / infrastructure problems
                if (
                    "429" in error
                    or "resource_exhausted" in error_lower
                    or "quota" in error_lower
                    or "gemini api error" in error_lower
                    or "unavailable" in error_lower
                    or "503" in error
                    or "service unavailable" in error_lower
                ):
                    api_failures += 1
                    print("RESULT: API/QUOTA FAILURE")

                # Java compilation problems
                elif "compilation" in status.lower():
                    compilation_failures += 1
                    print("RESULT: COMPILATION FAILURE")

                # Java execution problems
                else:
                    execution_failures += 1
                    print("RESULT: EXECUTION FAILURE")

                print(f"Error: {error}")

        except FileNotFoundError as error:
            test_errors += 1
            print("RESULT: TEST ERROR")
            print(f"File error: {error}")

        except Exception as error:
            test_errors += 1
            print("RESULT: TEST ERROR")
            print(f"Error: {error}")

    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    print(f"Total test cases        : {total}")
    print(f"Successful conversions  : {successful}")
    print(f"API/Quota failures      : {api_failures}")
    print(f"Compilation failures    : {compilation_failures}")
    print(f"Execution failures      : {execution_failures}")
    print(f"Test errors             : {test_errors}")

    if total > 0:
        success_rate = (successful / total) * 100
        print(f"Conversion success rate : {success_rate:.2f}%")

    print("=" * 60)


if __name__ == "__main__":
    main()
