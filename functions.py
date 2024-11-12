import streamlit as st
import pandas as pd
import time
from typing import List, Dict
from serpapi import GoogleSearch
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import os

def get_sheet_client():
    """Helper function to create authenticated Google Sheets client"""
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
        client = gspread.authorize(creds)
        
        # Get service account email for error messages
        service_account_email = creds.service_account_email
        st.session_state['service_account_email'] = service_account_email
        
        return client
    except FileNotFoundError:
        raise ValueError(
            "credentials.json file not found. Please ensure it exists in the project directory."
        )
    except Exception as e:
        raise ValueError(f"Error setting up Google Sheets client: {str(e)}")

def get_worksheet(sheet_id: str, range_name: str = None):
    """Helper function to get worksheet with improved error handling"""
    try:
        client = get_sheet_client()
        sheet = client.open_by_key(sheet_id)
        return sheet.worksheet(range_name) if range_name else sheet
    except gspread.exceptions.SpreadsheetNotFound:
        service_email = st.session_state.get('service_account_email', 'the service account')
        raise ValueError(
            f"Spreadsheet not found. Please verify:\n"
            f"1. The spreadsheet ID is correct\n"
            f"2. The sheet is shared with {service_email}\n"
            f"3. Sharing permissions allow edit access"
        )
    except gspread.exceptions.WorksheetNotFound:
        raise ValueError(f"Worksheet '{range_name}' not found in the spreadsheet")
    except gspread.exceptions.APIError as e:
        if 'PERMISSION_DENIED' in str(e):
            service_email = st.session_state.get('service_account_email', 'the service account')
            raise ValueError(
                f"Permission denied. Please share the spreadsheet with {service_email} "
                f"and ensure it has edit access."
            )
        raise ValueError(f"Google Sheets API error: {str(e)}")

def process_queries(df: pd.DataFrame, primary_column: str, query_template: str) -> List[Dict]:
    results = []
    
    serpapi_key = os.getenv("SERPAPI_API_KEY")  
    for index, row in df.iterrows():
        try:
            value = row[primary_column]
            query = query_template.replace(f"{{{primary_column}}}", str(value))
            
            # Perform search
            search = GoogleSearch({
                "q": query,
                "gl": "in",
                "api_key": serpapi_key,
                "num": 5  
            })
            search_results = search.get_dict()
            
            # Store results
            results.append({
                primary_column: value,
                "query": query,
                "search_results": search_results.get("organic_results", [])
            })
            
            # Rate limiting
            time.sleep(1) 
            
            
            if index % 10 == 0:  
                st.write(f"Processed {index + 1} queries...")
                
        except Exception as e:
            st.warning(f"Error processing query for {value}: {str(e)}")
            continue
    
    return results

def setup_llm():
    """Setup LangChain with Groq"""
    api_key=os.getenv("GROQ_API_KEY")
    llm = ChatGroq(
        api_key=api_key, 
        model="llama-3.1-8b-instant",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    return llm

def process_with_ai(search_results: dict, query: str, llm) -> str:
    template = """
    Extract ONLY the specific information requested from the search results for: {query}
    
    Search Results:
    {search_results}
    
    Provide ONLY the extracted information as a simple text response. 
    If multiple items exist, separate them with semicolons.
    If no relevant information is found, respond with "Not found".
    
    For example:
    - If asked for locations: "Bengaluru; Mumbai; Delhi"
    - If asked for email: "contact@company.com"
    - If asked for address: "123 Main Street, City, Country"
    """
    
    prompt = PromptTemplate(
        input_variables=["query", "search_results"],
        template=template
    )
    
    chain = prompt | llm
    response = chain.invoke({"query": query, "search_results": search_results})
    
    return response




def load_google_sheet(sheet_id: str, range_name: str) -> pd.DataFrame:    
    worksheet = get_worksheet(sheet_id,range_name)
    data = worksheet.get_all_records()    
    return pd.DataFrame(data)


def write_to_google_sheet(sheet_id: str, range_name: str, results_df: pd.DataFrame):

    worksheet = get_worksheet(sheet_id, range_name)
    
    all_values = worksheet.get_all_values()
    num_rows = len(all_values)
    next_col_num = len(all_values[0]) + 1
    next_col_letter = chr(64 + next_col_num) 
    
    range = f'{next_col_letter}1:{next_col_letter}{num_rows}'
    
    values = [['AI Results']] + [[str(result)] for result in results_df['result']]
    
    worksheet.update(values, f'{range}')


def get_all_sheet_names(sheet_id: str) -> List[str]:
    
    worksheet = get_worksheet(sheet_id)
    sheets = map(lambda x: x.title, worksheet.worksheets())
    return list(sheets)
