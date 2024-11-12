import streamlit as st
import pandas as pd
from functions import *
from dotenv import load_dotenv

load_dotenv()

def initialize_session_state():
    if 'processing_complete' not in st.session_state:
        st.session_state['processing_complete'] = False
    if 'results_df' not in st.session_state:
        st.session_state['results_df'] = None
    if 'output_choice' not in st.session_state:
        st.session_state['output_choice'] = "Download CSV"

initialize_session_state()

def main():
    st.title("InfoSynth")
    
    df = None
    
    # File upload section
    st.header("1. Upload Your Data")
    data_source = st.radio("Choose a data source:", ["CSV File", "Google Sheet"])

    if data_source == "CSV File":
        uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
    else:
        st.info(
        "Before proceeding, ensure your Google Sheet is shared with the service account. "
        "You can find the service account email in your credentials.json file."
        )
        spreadsheet_id = st.text_input(
            "Enter Google Spreadsheet ID", 
            help="You can find this in the spreadsheet URL between /d/ and /edit"
        )
        
        sheet_names = None
        if spreadsheet_id:
            try:
                sheet_names = get_all_sheet_names(spreadsheet_id)
                if not sheet_names:
                    st.error("No sheets found in this spreadsheet. Please check the ID and permissions.")
            except ValueError as e:
                st.error(f"Error accessing spreadsheet: {str(e)}")
                st.info("Please check the ID and permissions.")
            except Exception as e:
                st.error(f"Error accessing spreadsheet: {str(e)}")
                sheet_names = []
        
        sheet_name = None
        if sheet_names:
            sheet_name = st.selectbox(
                "Select Sheet Name",
                options=sheet_names,
                help="The name of the specific sheet to read from"
            )
        
        if spreadsheet_id and sheet_name:
            try:
                df = load_google_sheet(spreadsheet_id, sheet_name)
                if df is None or df.empty:
                    st.error("No data found in the selected sheet.")
            except Exception as e:
                st.error(f"Error loading sheet data: {str(e)}")
                df = None

    if df is not None:
        try:
            # Display available columns for selection
            st.header("2. Select Primary Column")
            primary_column = st.selectbox(
                "Choose the main column for analysis:",
                options=df.columns.tolist()
            )
            
            # Show data preview
            st.header("3. Data Preview")
            st.write("First 5 rows of your data:")
            st.dataframe(df.head())            
            
            # Add Query Template Section
            st.header("4. Query Template")
            st.write(f"""
            Create your query template using {primary_column} as a placeholder.
            Example: "What products does {primary_column} offer?"
            """)
            
            query_template = st.text_area(
                "Enter your query template:",
                value=f"Tell me about {{{primary_column}}}",
                help=f"Use {{{primary_column}}} as a placeholder"
            )
            
            # Preview generated queries
            #if st.button("Preview Generated Queries"):
            #    st.subheader("Generated Queries Preview")
            #    # Get first 5 values from the selected column
            #    sample_values = df[primary_column].head()
            #    
            #    # Display example queries
            #    for value in sample_values:
            #        generated_query = query_template.replace(
            #            f"{{{primary_column}}}", str(value)
            #        )
            #        st.write(f"- {generated_query}")
            #    
            #    # Show total number of queries that will be generated
            #    st.info(f"Total queries to be generated: {len(df)}")
            
            # Add confirmation and processing section
            st.header("5. Process Queries")
            total_queries = len(df[primary_column])
            estimated_time = total_queries * 2  # 2 second per query due to rate limiting
            
            st.warning(f"""
            ⚠️ Please confirm:
            - Number of queries to process: {total_queries}
            - Estimated processing time: {estimated_time} seconds ({estimated_time/60:.1f} minutes)
            - This will use {total_queries} API calls
            """)
            
            # Show sample of what will be processed
            #st.subheader("Sample of data to be processed:")
            #sample_df = df[[primary_column]].head()
            #st.dataframe(sample_df)
            
            # Process button with confirmation
            if st.button("Start Processing"):
                with st.spinner("Processing queries..."):
                    # Add a progress bar
                    progress_bar = st.progress(0)
                    
                    results = []
                    llm = setup_llm()
                    for index, row in df.iterrows():
                        try:
                            value = row[primary_column]
                            
                            # Handle empty/null values
                            if pd.isna(value) or str(value).strip() == '':
                                results.append({
                                    'input_value': value,
                                    'result': 'NA'
                                })
                                continue
                            
                            query = query_template.replace(f"{{{primary_column}}}", str(value))
                            
                            # Display current processing item
                            st.text(f"Processing: {value}")
                            
                            # Process query
                            result = process_queries(pd.DataFrame([row]), primary_column, query)
                            output = process_with_ai(result, query, llm)
                            
                            results.append({
                                'input_value': value,
                                'result': output.content
                            })
                            
                            # Update progress
                            progress_bar.progress((index + 1) / total_queries)
                            
                        except Exception as e:
                            st.error(f"Error processing {value}: {str(e)}")
                            continue
                    
                    # Show completion and results
                    st.session_state['processing_complete'] = True
                    st.session_state['results_df'] = pd.DataFrame(results, columns=['input_value', 'result'])

            # Show results and save options if processing is complete
            if st.session_state['processing_complete']:
                st.success(f"✅ Completed processing {len(st.session_state['results_df'])} queries!")
                
                st.subheader("Results Preview:")
                st.dataframe(st.session_state['results_df'].head())
                
                st.header("6. Save Results")
                output_choice = st.radio("Choose an output format:", ["Download CSV", "Update Google Sheet"])

                if output_choice == "Download CSV":
                    csv = st.session_state['results_df'].to_csv(index=False)
                    if st.download_button(
                        "Download Complete Results (CSV)",
                        csv,
                        "search_results.csv",
                        "text/csv",
                        key='download-csv'
                    ):
                        st.success("✅ File downloaded successfully!")
                        
                elif output_choice == "Update Google Sheet":
                    update_button = st.button("Confirm Update to Google Sheet")
                    if update_button:
                        try:
                            write_to_google_sheet(spreadsheet_id, sheet_name, st.session_state['results_df'])
                            st.success("✅ Results successfully added as new column!")
                        except Exception as e:
                            st.error(f"Error updating sheet: {str(e)}")
        except Exception as e:
            st.error(f"Error processing the file: {str(e)}")

if __name__ == "__main__":
    main()
