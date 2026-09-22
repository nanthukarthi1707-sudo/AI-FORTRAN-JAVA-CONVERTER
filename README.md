# 🤖 AI-Powered FORTRAN to Java Code Converter

An AI-powered legacy code modernization tool that converts FORTRAN programs into modern Java source code using Google's Gemini API.

The system reads FORTRAN source code, sends it to a Gemini LLM with a structured conversion prompt, generates Java code, validates the generated code using the Java compiler, and executes the compiled Java program.

---

## 📌 Project Overview

Many legacy scientific, engineering, and enterprise systems still contain FORTRAN code. Migrating such systems manually to modern programming languages can require significant time and effort.

This project explores an AI-assisted approach for modernizing legacy FORTRAN programs into Java.

### Project Workflow

```text
FORTRAN Source Code
        ↓
Streamlit Web Interface
        ↓
Python Preprocessing
        ↓
Gemini LLM
        ↓
Generated Java Code
        ↓
Java Code Cleaning
        ↓
Java Compilation (javac)
        ↓
Java Execution
        ↓
Output / Validation