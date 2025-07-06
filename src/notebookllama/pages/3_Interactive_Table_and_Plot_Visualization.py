import sys
import os
import io
import tempfile as tmp

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from utils import get_plots_and_tables
import streamlit as st
from PIL import Image


def get_plots_and_tables_sync(file: io.BytesIO):
    fl = tmp.NamedTemporaryFile(suffix=".pdf", delete=False, delete_on_close=False)
    with open(fl.name, "wb") as f:
        f.write(file.getvalue())

    # Try to get existing event loop, if not create a new one
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("Event loop is closed")
    except RuntimeError:
        # No event loop exists or it's closed, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Run the async function in the current event loop
    if loop.is_running():
        # If loop is already running (e.g., in Jupyter/Streamlit),
        # we need to use a different approach
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                asyncio.run, get_plots_and_tables(file_path=fl.name)
            )
            return future.result()
    else:
        # If loop is not running, we can use it directly
        return loop.run_until_complete(get_plots_and_tables(file_path=fl.name))


def cleanup_temp_files(image_paths):
    """Clean up temporary image files"""
    for img_path in image_paths:
        try:
            if os.path.exists(img_path):
                os.remove(img_path)
        except Exception as e:
            st.warning(f"Could not remove {img_path}: {str(e)}")


def create_download_zip(dataframes, image_paths):
    """Create a ZIP file with all extracted data"""
    import zipfile

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Add CSV files
        for i, df in enumerate(dataframes):
            csv_data = df.to_csv(index=False)
            zip_file.writestr(f"table_{i + 1}.csv", csv_data)

        # Add image files
        for i, img_path in enumerate(image_paths):
            if os.path.exists(img_path):
                file_ext = os.path.splitext(img_path)[1]
                zip_file.write(img_path, f"image_{i + 1}{file_ext}")

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


# Direct Streamlit execution
# Chat Interface
st.set_page_config(page_title="NotebookLlaMa - Images and Tables", page_icon="📊")

st.sidebar.header("Images and Tables📊")
st.sidebar.info("To switch to the Home page, select it from above!🔺")
st.markdown("---")
st.markdown("## NotebookLlaMa - Images and Tables📊")
st.markdown("### Upload a PDF file to extract plots and tables")

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Process the file
    with st.spinner("Processing PDF... This may take a moment."):
        try:
            # Convert uploaded file to BytesIO
            file_bytes = io.BytesIO(uploaded_file.getvalue())

            # Extract plots and tables
            image_paths, dataframes = get_plots_and_tables_sync(file_bytes)

            # Display results summary
            st.success("✅ Processing complete!")
            st.info(f"Found {len(image_paths)} images and {len(dataframes)} tables")

            # Create tabs for better organization
            tab1, tab2 = st.tabs(["📊 Tables", "📈 Plots/Images"])

            with tab1:
                st.header("Extracted Tables")
                if dataframes:
                    for i, df in enumerate(dataframes):
                        st.subheader(f"Table {i + 1}")

                        # Display table with options
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.dataframe(df, use_container_width=True)

                        with col2:
                            st.write("**Table Info:**")
                            st.write(f"Rows: {len(df)}")
                            st.write(f"Columns: {len(df.columns)}")

                            # Download button for CSV
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name=f"table_{i + 1}.csv",
                                mime="text/csv",
                                key=f"download_table_{i}",
                            )

                        # Show additional table statistics
                        with st.expander(f"Table {i + 1} Details"):
                            st.write("**Column Information:**")
                            st.write(df.dtypes)
                            st.write("**First few rows:**")
                            st.write(df.head())
                            if len(df) > 5:
                                st.write("**Summary statistics:**")
                                st.write(df.describe(include="all"))

                        st.divider()
                else:
                    st.warning("No tables found in the PDF")

            with tab2:
                st.header("Extracted Plots and Images")
                if image_paths:
                    for i, img_path in enumerate(image_paths):
                        st.subheader(f"Image {i + 1}")

                        try:
                            # Display image
                            if os.path.exists(img_path):
                                image = Image.open(img_path)

                                # Create columns for image and info
                                col1, col2 = st.columns([3, 1])

                                with col1:
                                    st.image(
                                        image,
                                        caption=f"Image {i + 1}",
                                        use_container_width=True,
                                    )

                                with col2:
                                    st.write("**Image Info:**")
                                    st.write(f"Size: {image.size}")
                                    st.write(f"Format: {image.format}")
                                    st.write(f"Mode: {image.mode}")

                                    # Download button for image
                                    with open(img_path, "rb") as file:
                                        st.download_button(
                                            label="Download Image",
                                            data=file.read(),
                                            file_name=f"image_{i + 1}.{image.format.lower()}",
                                            mime=f"image/{image.format.lower()}",
                                            key=f"download_image_{i}",
                                        )

                                st.divider()
                            else:
                                st.error(f"Image file not found: {img_path}")

                        except Exception as e:
                            st.error(f"Error loading image {i + 1}: {str(e)}")
                else:
                    st.warning("No images found in the PDF")

            # Cleanup section
            st.header("📂 File Management")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("🗑️ Clean up temporary files"):
                    cleanup_temp_files(image_paths)
                    st.success("Temporary files cleaned up!")

            with col2:
                # Option to download all data as ZIP
                if st.button("📦 Download All Data"):
                    zip_data = create_download_zip(dataframes, image_paths)
                    st.download_button(
                        label="Download ZIP",
                        data=zip_data,
                        file_name="extracted_data.zip",
                        mime="application/zip",
                    )

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.exception(e)  # Show full traceback in development
