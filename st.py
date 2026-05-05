import io
from typing import Optional
import streamlit as st
from Engine import analyze_commentary_score

try:
    from pypdf import PdfReader
except ImportError:  # Optional dependency for PDF support
    PdfReader = None


def read_txt_file(file_bytes: bytes) -> str:
    """Decode uploaded txt file content."""
    return file_bytes.decode("utf-8", errors="replace")


def read_pdf_file(file_bytes: bytes) -> str:
    """Extract text from uploaded PDF file content."""
    if PdfReader is None:
        return "PDF support needs `pypdf`.\nInstall it with: pip install pypdf"

    pdf = PdfReader(io.BytesIO(file_bytes))
    pages_text = []
    for page in pdf.pages:
        pages_text.append(page.extract_text() or "")
    return "\n".join(pages_text).strip()


def get_uploaded_file_text(uploaded_file) -> Optional[str]:
    """Return parsed text from txt/pdf uploads."""
    if uploaded_file is None:
        return None

    file_bytes = uploaded_file.read()
    name = uploaded_file.name.lower()

    if name.endswith(".txt"):
        return read_txt_file(file_bytes)

    if name.endswith(".pdf"):
        return read_pdf_file(file_bytes)

    return "Unsupported file format. Please upload a .txt or .pdf file."


def main() -> None:
    st.set_page_config(
        page_title="Commentary Score Analyzer", page_icon="🏏", layout="centered"
    )
    st.title("Text or File Input")
    st.write("Provide text directly, or upload a `.txt` / `.pdf` file.")

    input_mode = st.radio(
        "Choose input method:",
        ("Type text", "Upload file"),
        horizontal=True,
    )

    final_text = ""

    if input_mode == "Type text":
        final_text = st.text_area(
            "Enter your text:",
            height=220,
            placeholder="Type your text here...",
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload a file (.txt or .pdf)",
            type=["txt", "pdf"],
            accept_multiple_files=False,
        )
        parsed_text = get_uploaded_file_text(uploaded_file)
        if parsed_text is not None:
            final_text = parsed_text
            st.success("File processed successfully.")
            st.text_area("Extracted text:", value=final_text, height=220)

    if st.button("Submit"):
        if final_text.strip():
            with st.spinner("Analyzing commentary..."):
                result = analyze_commentary_score(final_text)

            if result.get("ok"):
                st.subheader("Model Output")
                st.code(result["analysis"], language="json")

                st.subheader("Run Metrics")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Time Taken (s)", f"{result['elapsed_seconds']:.2f}")
                c2.metric("Total Tokens", str(result["total_tokens"]))
                c3.metric(
                    "Estimated Cost (USD)", f"${result['estimated_cost_usd']:.6f}"
                )
                c4.metric(
                    "Estimated Cost (INR)", f"₹{result['estimated_cost_inr']:.2f}"
                )
            else:
                st.error(f"Analysis failed: {result.get('error', 'Unknown error')}")
                st.write(f"Time Taken: {result['elapsed_seconds']:.2f}s")
        else:
            st.warning("Please provide text or upload a supported file first.")


if __name__ == "__main__":
    main()
