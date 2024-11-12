# InfoSynth

InfoSynth is a powerful data enrichment tool that combines web search capabilities with AI processing to extract structured information from unstructured web data. Built with Streamlit, it supports both CSV files and Google Sheets as data sources.

## Features

- Data source flexibility: Upload CSV files or connect directly to Google Sheets
- Automated web searching using SerpAPI
- AI-powered information extraction using Groq LLM
- Progress tracking and error handling
- Export results to CSV or directly to Google Sheets
- Interactive query preview and customization

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/Umang-Bansal/infosynth.git
cd infosynth
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up API credentials:
   - Create a `credentials.json` file for Google Sheets API access (see Google Sheets Setup section)
   - Obtain API keys for:
     - SerpAPI (for web searching)
     - Groq (for AI processing)

4. Configure environment variables:
   - Create a `.env` file in the project root directory
   - Add the following variables:
     ```
     SERPAPI_API_KEY=your_serpapi_key
     GROQ_API_KEY=your_groq_api_key
     ```

## Usage Guide

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Follow the web interface steps:
   - Choose data source (CSV or Google Sheets)
   - If using Google Sheets:
     - Enter the Spreadsheet ID (found in the sheet's URL)
     - Select the specific sheet name
   - Select the primary column for analysis
   - Customize your query template
   - Review the generated queries and estimated processing time
   - Start processing
   - Export results in your preferred format (CSV or update Google Sheet)

## Google Sheets Setup

1. Create a Google Cloud Project and enable the Google Sheets API
2. Create a service account and download the credentials.json file
3. Place the credentials.json file in your project root directory
4. Share your Google Sheet with the service account email address

### Sharing Your Google Sheet

1. Open your Google Sheet
2. Click the "Share" button in the top right
3. Add the service account email as an Editor
   - The email can be found in your credentials.json file
   - It typically ends with @*.iam.gserviceaccount.com
4. Click "Send" (no need to actually send an email)

## API Keys and Environment Variables

- SerpAPI Key: Sign up at [SerpAPI](https://serpapi.com/) to get your API key
- Groq API Key: Obtain your key from [Groq](https://groq.com/)
- Add both keys to your `.env` file as shown in the Setup Instructions

## Optional Features

- Dynamic query preview: See example queries generated from your data in real-time
- Progress tracking: Visual progress bar and status updates during processing
- Error handling: Detailed error messages and graceful failure recovery
- Google Sheets integration: Direct reading and writing to Google Sheets

## Troubleshooting

If you encounter permission errors with Google Sheets:
1. Verify the spreadsheet ID is correct
2. Confirm the sheet is shared with the correct service account email
3. Ensure the service account has Editor access
4. Check that your credentials.json file is properly configured

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
