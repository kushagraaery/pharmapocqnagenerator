import openai
import streamlit as st
import pandas as pd
from io import BytesIO
import os
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Streamlit UI Enhancements
st.set_page_config(page_title="Pharma Society QnA Report Generator", page_icon="💊")

# Inline CSS for styling
st.markdown("""
    <style>
        /* General app styles */
        body {
            background-color: #f9f9f9;
            font-family: "Arial", sans-serif;
        }
        .main-header {
            font-size: 3rem;
            color: #FFA500;
            text-align: center;
            margin-bottom: 1rem;
            animation: fadeIn 6s;
        }
        .prompt-buttons button {
            background-color: #007bff;
            color: white;
            border: none;
            font-size: 1rem;
            padding: 10px 15px;
            border-radius: 5px;
            margin: 5px;
            cursor: pointer;
            transition: background-color 0.3s, transform 0.3s;
        }
        .prompt-buttons button:hover {
            background-color: #0056b3;
            transform: scale(1.05);
        }
        .table-container {
            margin: 20px 0;
        }
        .table-container .stDataFrame {
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .download-btn {
            display: inline-block;
            background-color: #28a745;
            color: white;
            padding: 10px 20px;
            font-size: 1rem;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 10px;
            transition: background-color 0.3s, transform 0.3s;
        }
        .download-btn:hover {
            background-color: #218838;
            transform: scale(1.05);
        }
        .fadeIn {
            animation: fadeIn 2s;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
""", unsafe_allow_html=True)

# Pharma Society Q&A Generator Section
st.markdown('<div class="main-header">💊 Pharma Society QnA Report Generator</div>', unsafe_allow_html=True)
st.write("🔬 This Q&A generator allows users to fetch answers to predefined queries about pharmaceutical societies by entering the society name in the text box. It uses OpenAI to generate answers specific to the entered society and displays them in a tabular format. Users can download this report as an Excel file.")

# Step 1: Initialize session state to track selected societies and report data
if "selected_societies" not in st.session_state:
    st.session_state.selected_societies = []
if "report_data" not in st.session_state:
    st.session_state.report_data = pd.DataFrame(columns=[
        "Society Name",
        "What is the membership count for society_name? Respond with one word (number) only.",
        "Does society_name encompasses community sites? Respond one word ('yes' or 'no') only plus provide a justification for the answer also after a comma.",
        "Is society_name influential on state or local policy? Respond one word ('yes' or 'no') only plus provide a justification for the answer also after a comma.",
        "Does society_name provide engagement opportunity with leadership? Respond one word ('yes' or 'no') only plus provide a justification for the answer also after a comma.",
        "Does society_name provide support for clinical trial recruitment? Respond one word ('yes' or 'no') only plus provide a justification for the answer also after a comma.",
        "Does society_name provide engagement opportunity with payors? Respond one word ('yes' or 'no') only plus provide a justification for the answer also after a comma.",
        "Does society_name include area experts on its board? Respond one word ('yes' or 'no') only plus provide a justification for the answer also after a comma.",
        "Is society_name involved in therapeutic research collaborations? Respond one word ('yes' or 'no') only plus provide a justification for the answer also after a comma.",
        "Does society_name include top therapeutic area experts on its board? Respond with one word ('yes' or 'no') only plus provide a justification for the answer also after a comma.",
        "Name the Region where the society_name is from? Just name the Region in word for the answer."
    ])

# Define all available society options
all_societies = [
    "Soleo Health",
    "Asociacion Puertorriquena De Hemofilia Inc",
    "Dava Oncology, LP",
    "University of Miami",
    "Florida Society of Clinical Oncology Inc",
    "Blue Cross Blue Shield Association",
    "Florida Society of Pathologists",
    "Florida Gastroenterologic Society",
    "Horizon CME",
    "Florida Society of Ophthamology",
    "HealioLive",
    "Mayo Clinic Jacksonville",
    "Fundacion De Esclerosis Multiple de Puerto Rico",
    "American Academy of Pediatrics Georgia Chapter",
    "Large Urology Group Practice Association",
    "Cancer Specialists of NE/FL",
    "THE MEDICAL EDUCATOR CONSORTIUM INC.",
    "Florida Society of Health-System Pharmacists Inc",
    "American Geriatrics Society Inc",
    "National Multiple Sclerosis Society",
    "Florida Society Dermatology Physician Assistant",
    "Hemophilia Foundation of Greater Florida Inc.",
    "Foundation Hope & Life USA",
    "Florida Nurse Practitioner Network Inc",
    "American Lung Association",
    "Gerontological Advanced Practice Nurses Association",
    "Georgia Society of Dermatology and Dermatologic Surgery Inc",
    "Intellisphere, LLC | Oncology Specialty Group",
    "Florida Allergy Asthma & Immunology Society Inc",
    "Florida Society of Rheumatology Inc",
    "American Retina Forum, Inc.",
    "Sociedad Puertorriqeña de Oftalmologia",
    "American Society for Mohs Surgery",
    "American Association of Nurses Practitioners Inc",
    "Southern Baptist Hospital of Florida Inc",
    "American College of Rheumatology",
    "Southeast Society of Health-System Pharmacists",
    "Bascom Palmer Eye Institute",
    "South Broward Hospital District/ Memorial Healthcare System",
    "American Association for Cancer Research",
    "H Lee Moffitt Cancer Center and Research Institute Foundation Inc",
    "Boca Raton Regional Hospital Foundation Inc",
    "Asociación Puertorriqueña de Médicos Alergistas",
    "Sociedad Dermatologica de Puerto Rico",
    "Society of Gynecologic Oncology",
    "Florida Society of Neurology",
    "Eastern Allergy Conference Inc",
    "Coalicion De Asma De Puerto Rico",
    "Allergy Education Partners",
    "FLORIDA BLEEDING DISORDERS ASSOCIATION, INC",
    "Oncology Nursing Society - Miami Dade Chapter",
    "American Association of Critical Care Nurses",
    "Palm Beach Society of Health System Pharmacists",
    "HMP Education, LLC",
    "Lulac Institute, Inc.",
    "Academia Puertorriqueña de Neurología",
    "National Community Oncology Dispensing Association",
    "The Womens Breast & Heart Initiative Florida Affiliate Inc",
    "MS Views and News, Inc",
    "Hemostasis and Thrombosis Research Society Inc",
    "Harborside Press LLC",
    "Mount Sinai Medical Center of Florida Inc",
    "International Physician Networks, LLC",
    "Florida Society of Oncology Social Workers",
    "University of Florida Jacksonville Physicians Inc",
    "Total Health Conferencing",
    "DeMarse Meetings and Events Agency",
    "Adventist Health System-Sunbelt Inc",
    "Association of Neurovascular Clinicians",
    "Susan G. Komen Breast Cancer Foundation, Inc., National Office",
    "International Society of Liquid Biopsy",
    "American Cancer Society, Inc.",
    "University of Florida",
    "Usf Health Professions Conferencing Corporation",
    "The Donna Foundation, Inc",
    "Southern Thoracic Surgical Association Inc",
    "Eastern Cardiothoracic Surgical Society",
    "World Events Forum, Inc.",
    "Tallahassee Memorial Healthcare Foundation Inc",
    "Central Florida Association of Physicians From The Indian Subcontinent (CAPI)",
    "H Lee Moffitt Cancer Center and Research Institute Hospital Inc",
    "Cure SMA",
    "Veritas Productions Partners, LLC",
    "Macula Society Inc",
    "NeuroNet Pro, LLC",
    "The Cleveland Clinic Educational Foundation",
    "Baptist Health South Florida Foundation Inc",
    "Memorial Foundation, Inc.",
    "Dolphins Cycling Challenge Inc",
    "General Thoracic Surgical Club",
    "Community Oncology Alliance Inc",
    "A Breath of Hope Lung Foundation",
    "GO2 Foundation for Lung Cancer",
    "Georgia Society of Ophthalmology",
    "Slack Events LLC",
    "Johns Hopkins All Children’s Foundation",
    "Academy of Oncology Nurse Navigators Inc",
    "Palm Beach Cancer Institute Foundation Inc",
    "Florida Cancer Specialists Foundation Inc.",
    "Association of Operating Room Nurses of Tampa Bay Inc",
    "Florida Association for the Study of Headache and Other Neurological Disorder",
    "Powers Meeting Management",
    "Hemophilia Federation of America",
    "Baptist Health System Inc",
    "The Leukemia & Lymphoma Society, Inc.",
    "American Tamil Medical Association",
    "Tampa Alumni Chapter of Kappa Alpha Psi Fraternity inc",
    "Foundation Fighting Blindness, Inc.",
    "UNIVERSITY OF MIAMI, UMiami Medicine - Ophthalmology (MIAMI), Bascom Palmer Eye Institute",
    "Jupiter Medical Center Inc",
    "Women in Ophthalmology Inc",
    "Black Health Matters Foundation Inc",
    "University of South Florida",
    "Gilda's Club of South Florida, Inc.",
    "Oncology Nursing Society",
    "JADPRO via BroadcastMed LLC",
    "Paralyzed Veterans of America",
    "Black Nurse Practitioners of Palm Beach County",
    "Bendcare LLC",
    "Pulmonary Fibrosis Foundation",
    "Association of VA Hematology Oncology Inc",
    "Dietz Farrell Inc",
    "Mayo Clinic Arizona",
    "Westside Regional Medical Staff Inc",
    "Vital Care",
    "Sharsheret, Inc.",
    "Society of Vascular and Interventional Neurology",
    "Neuromuscular Study Group",
    "American Association of Pharmaceutical Scientists",
    "Muscular Dystrophy Association",
    "EXCEL CONTINUING EDUCATION",
    "Baptist Health Foundation",
    "Johns Hopkins All Childrens Hospital Inc",
    "Americas Committee For Treatment & Research In Multiple Sclerosis Inc",
    "Florida Health Sciences Center Inc",
    "Rilite Foundation",
    "American Academy of Pediatrics - National",
    "Americas Hepato-Pancreato-Biliary Association Inc",
    "Foundation for Research and Education in Dermatology",
    "Chinese American Hematologist and Oncologist Network Inc",
    "Baptist Health of South Florida Inc",
    "National Association of Managed Care Physicians Inc",
    "Hematology Oncology Pharmacy Association Inc",
    "American Council of the Blind",
    "Ultimate Opinions in Medicine, LLC; dba PresiCa",
    "University of Florida Foundation, Inc.",
    "Can Do Multiple Sclerosis",
    "Florida Society of Dermatologic Surgeons",
    "American Oncology Network, LLC",
    "American Legion Post 390 Wellington Inc.",
    "HealthTrust Purchasing Group, LP",
    "Omega Psi Phi Fraternity, Inc",
    "Georgia Society of Rheumotology",
    "National Association of Health Services Executives Inc",
    "LATINOUS NFP",
    "Multiple Sclerosis Foundation, Inc.",
    "Univision of New Jersey Inc dba WXTV, WUVP, WFUT, WFPA",
    "Imedex",
    "Fellows Forum Inc",
    "The Sumaira Foundation",
    "Cardinal Health 119, LLC",
    "Asociacion de Hematologia Y Oncologia Medica de PR",
    "McKesson Specialty Health Pharmaceutical & Biotech Solutions LLC",
    "Memorial Health Systems Inc",
    "Tampa Food Allergy Support and Education",
    "Central Florida Health Care Coalition, Incorporated (Florida Alliance for Healthcare Value)",
    "Hope Charities",
    "Kentucky Medical Association",
    "National Organization of Rheumatology Managers",
    "India Association Cultural and Education Center of N Central FL I",
    "Acuity GPO LLC",
    "ACHE of South Florida"
]

# Step 2: Filter dropdown options to exclude already selected societies
available_societies = [society for society in all_societies if society not in st.session_state.selected_societies]
society_name = st.selectbox("Select the Pharmaceutical Society Name:", [""] + available_societies)

# Define updated pharma-specific questions for the society
questions = [
    "What is the membership count for society_name? Respond with one word (number) only.",
    "Does society_name encompasses community sites? Respond one word ('yes' or 'no') only plus provide a justification for the answer also after a comma.",
    "Is society_name influential on state or local policy? Respond one word ('yes' or 'no') only plus provide a justification for the answer also after a comma.",
    "Does society_name provide engagement opportunity with leadership? Respond one word ('yes' or 'no') only plus provide a justification for the answer also after a comma.",
    "Does society_name provide support for clinical trial recruitment? Respond one word ('yes' or 'no') only plus provide a justification for the answer also after a comma.",
    "Does society_name provide engagement opportunity with payors? Respond one word ('yes' or 'no') only plus provide a justification for the answer also after a comma.",
    "Does society_name include area experts on its board? Respond one word ('yes' or 'no') only plus provide a justification for the answer also after a comma.",
    "Is society_name involved in therapeutic research collaborations? Respond one word ('yes' or 'no') only plus provide a justification for the answer also after a comma.",
    "Does society_name include top therapeutic area experts on its board? Respond with one word ('yes' or 'no') only plus provide a justification for the answer also after a comma.",
    "Name the Region where the society_name is from? Just name the Region in word for the answer."
]

# Function to fetch data from OpenAI
def fetch_society_data(society):
    if society in st.session_state.selected_societies:
        return  # Skip if already fetched

    st.session_state.selected_societies.append(society)
    society_data = {"Society Name": society}
    modified_questions = [q.replace("society_name", society) for q in questions]

    with st.spinner(f"Fetching data for {society}..."):
        for i, question in enumerate(modified_questions):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": question}]
                )
                answer = response["choices"][0]["message"]["content"].strip()
                society_data[questions[i]] = answer
            except Exception as e:
                st.error(f"Error fetching data for '{society}': {e}")
                society_data[questions[i]] = "Error"

    st.session_state.report_data = pd.concat([st.session_state.report_data, pd.DataFrame([society_data])], ignore_index=True)

# Fetch data for selected society
if society_name and st.button("Fetch Data for Selected Society"):
    fetch_society_data(society_name)

# Fetch data for all societies at once
if st.button("Fetch Data for All Societies"):
    with st.spinner("Fetching data for all societies..."):
        for society in all_societies:
            fetch_society_data(society)

# Display consolidated report
if not st.session_state.report_data.empty:
    st.write("📊 **Consolidated Tabular Report:**")
    st.dataframe(st.session_state.report_data)

    # Function to export DataFrame as Excel
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="Consolidated Report")
        return output.getvalue()

    excel_data = to_excel(st.session_state.report_data)

    st.download_button(
        label="⬇️ Download Consolidated Report",
        data=excel_data,
        file_name="Consolidated_Pharma_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def send_email(smtp_server, smtp_port, sender_email, sender_password, receiver_email, subject, html_content):
    # Create the email message
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_content, "html"))

    # Choose whether to use SSL or TLS
    try:
        if smtp_port == 465:  # Use SSL
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
        elif smtp_port == 587:  # Use TLS
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(sender_email, sender_password)
                server.send_message(msg)
        return "Email sent successfully!"
    except Exception as e:
        return f"Failed to send email: {e}"

# HTML Table Conversion (for email body)
def dataframe_to_html(df):
    return df.to_html(index=False, border=1, classes="dataframe", justify="center")

# Email Sending Interface
if not st.session_state.report_data.empty:
    # st.write("📧 Email Report:")

    # Collect email details from user input
    receiver_email = "goyals14@gene.com"
    email_subject = "Consolidated Pharma Society Report"

    # Set Gmail SMTP server settings
    smtp_server = "smtp.gmail.com"  # Gmail SMTP server
    smtp_port = 587  # Choose SSL or TLS

    # Set your sender email here (e.g., your Gmail)
    sender_email = "johnwickcrayons@gmail.com"
    sender_password = "afpt eoyt asaq qzjh"

    # Send email if button clicked
    if st.button("Send data to Google Sheets"):
        if receiver_email and email_subject and sender_email and sender_password:
            html_table = dataframe_to_html(st.session_state.report_data)
            email_body = f"""
            <html>
            <head>
                <style>
                    .dataframe {{
                        font-family: Arial, sans-serif;
                        border-collapse: collapse;
                        width: 100%;
                    }}
                    .dataframe td, .dataframe th {{
                        border: 1px solid #ddd;
                        padding: 8px;
                    }}
                    .dataframe tr:nth-child(even) {{
                        background-color: #f2f2f2;
                    }}
                    .dataframe th {{
                        padding-top: 12px;
                        padding-bottom: 12px;
                        text-align: left;
                        background-color: #4CAF50;
                        color: white;
                    }}
                </style>
            </head>
            <body>
                <p>Dear Recipient,</p>
                <p>Find the attached consolidated report below:</p>
                {html_table}
                <p>Best regards,<br>Pharma Society Insights Team</p>
            </body>
            </html>
            """
            status = send_email(smtp_server, smtp_port, sender_email, sender_password, receiver_email, email_subject, email_body)

            # Display success or error message
            if "successfully" in status:
                st.success("Successfully sent data to Google Sheets!")
            else:
                st.error("Error while appending data to Google Sheets!")

# Chatbot 2.0 Section with Enhanced Styling and Animations
st.markdown('<div class="main-header">🤖 Chatbot 2.0 - Fine-Tuned on Report Data</div>', unsafe_allow_html=True)
st.markdown("📋 This chatbot uses OpenAI and the **consolidated report** data to answer your queries.")

# Custom CSS for chatbot styling and animations
st.markdown("""
    <style>
        .chat-container {
            border: 2px solid #007bff;
            border-radius: 10px;
            padding: 15px;
            background-color: #f8f9fa;
            margin-bottom: 20px;
        }
        .chat-container h3 {
            color: #007bff;
            margin-bottom: 10px;
        }
        .user-message, .assistant-message {
            display: flex;
            align-items: flex-start;
            margin-bottom: 15px;
        }
        .user-message {
            animation: slideInRight 0.5s;
        }
        .assistant-message {
            animation: slideInLeft 0.5s;
        }
        .chat-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-right: 10px;
            background-size: cover;
        }
        .user-avatar {
            background-image: url('https://via.placeholder.com/40/007bff/ffffff?text=U');
        }
        .assistant-avatar {
            background-image: url('https://via.placeholder.com/40/28a745/ffffff?text=A');
        }
        .chat-bubble {
            max-width: 75%;
            padding: 10px 15px;
            border-radius: 15px;
            font-size: 0.95rem;
            box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
        }
        .user-message .chat-bubble {
            background-color: #007bff;
            color: white;
            border-top-left-radius: 0;
        }
        .assistant-message .chat-bubble {
            background-color: #e9ecef;
            color: #212529;
            border-top-right-radius: 0;
        }
        .fadeIn {
            animation: fadeIn 0.8s ease-in-out;
        }
        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideInLeft {
            from { transform: translateX(-100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for Chatbot 2.0 messages
if "messages_2" not in st.session_state:
    st.session_state["messages_2"] = [
        {"role": "assistant", "content": "I am here to answer questions based on your consolidated report. How can I help you?"}
    ]

# Chatbot 2.0 input box
chat_input_2 = st.chat_input("Ask a question about the consolidated report...")

# Format the report data as a context for OpenAI
def format_report_for_context(df):
    if df.empty:
        return "No report data is currently available."
    context = "Here is the consolidated report data:\n"
    for _, row in df.iterrows():
        context += f"Society Name: {row['Society Name']}\n"
        for col in df.columns[1:]:  # Skip 'Society Name'
            context += f"  {col}: {row[col]}\n"
        context += "\n"
    return context.strip()

# Generate a response from OpenAI based on the report and user query
def generate_openai_response(query, report_context):
    try:
        # Construct a dynamic prompt
        prompt = f"""
         You are an AI assistant fine-tuned to answer questions based on a pharmaceutical society consolidated report. 
         Use the following report data to answer user queries accurately if the information exists in the report.
         If the query cannot be answered using the report, respond using your general knowledge i.e. using chat-gpt model:
        
        {report_context}
        
        User's question: {query}
        
        Respond concisely using the data provided.
        """
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            #   model="gpt-4",
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}]
        )
        return response.choices[0]["message"]["content"].strip()
    except Exception as e:
        return f"Error generating response: {e}"

# Predefined Prompt Buttons in a grid
st.markdown('<div class="prompt-buttons">', unsafe_allow_html=True)
cols = st.columns(3)

with cols[0]:
    if st.button("List down all the societies inside the Report."):
        chat_input_2 = "List down all the societies inside the Report only if there is report data."
with cols[1]:
    if st.button("Which Society do you think is the best out of all and why?"):
        chat_input_2 = "Which Society do you think is the best out of all and why only if there is report data?"
with cols[2]:
    if st.button("Tell me the society names with highest and lowest count of membership."):
        chat_input_2 = "Tell me the society names with highest and lowest count of membership only if there is report data."
st.markdown('</div>', unsafe_allow_html=True)

# Process Chatbot 2.0 input
if chat_input_2:
    st.session_state["messages_2"].append({"role": "user", "content": chat_input_2})

    # Prepare report data as context
    report_context = format_report_for_context(st.session_state.report_data)

    # Generate a response using OpenAI
    with st.spinner("Generating response..."):
        bot_reply_2 = generate_openai_response(chat_input_2, report_context)

    st.session_state["messages_2"].append({"role": "assistant", "content": bot_reply_2})

# Display Chatbot 2.0 conversation with new styling
for msg in st.session_state["messages_2"]:
    if msg["role"] == "user":
        st.markdown(
            f"""
            <div class="user-message">
                <div class="chat-avatar user-avatar"></div>
                <div class="chat-bubble">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True
        )
    elif msg["role"] == "assistant":
        st.markdown(
            f"""
            <div class="assistant-message">
                <div class="chat-avatar assistant-avatar"></div>
                <div class="chat-bubble">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True
        )
st.markdown('</div>', unsafe_allow_html=True)

# Header section
st.markdown('<div class="main-header">💬 Pharma Insights Chatbot </div>', unsafe_allow_html=True)
st.markdown('💡 This app features a chatbot powered by OpenAI for answering society-related queries.', unsafe_allow_html=True)

# Predefined Prompt Buttons in a grid
st.markdown('<div class="prompt-buttons">', unsafe_allow_html=True)
cols = st.columns(3)

prompt = None

with cols[0]:
    if st.button("What are the top 10 oncology societies in California actively supporting clinical trials and research initiatives?"):
        prompt = "What are the top 10 oncology societies in California actively supporting clinical trials and research initiatives?"
with cols[1]:
    if st.button("Which Oncology Society in the World has the largest membership network and reach?"):
        prompt = "Which Oncology Society in the World has the largest membership network and reach?"
with cols[2]:
    if st.button("Which Oncology Societies in California collaborate with pharmaceutical companies for drug development initiatives?"):
        prompt = "Which Oncology Societies in California collaborate with pharmaceutical companies for drug development initiatives?"

# Add additional buttons in another row
cols = st.columns(3)
with cols[0]:
    if st.button("List the Oncology Societies in California that offer leadership opportunities for healthcare professionals."):
        prompt = "List the Oncology Societies in California that offer leadership opportunities for healthcare professionals."
with cols[1]:
    if st.button("Which Oncology Societies in California are most active in influencing state healthcare policies?"):
        prompt = "Which Oncology Societies in California are most active in influencing state healthcare policies?"
with cols[2]:
    if st.button("Identify oncology societies in California that provide resources or support for community-based oncology practices."):
        prompt = "Identify oncology societies in California that provide resources or support for community-based oncology practices."
st.markdown('</div>', unsafe_allow_html=True)

# Chat Input Section
user_input = st.chat_input("Ask a question or select a prompt...")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I assist you today?"}]

# Append user input or prompt to chat history
if prompt or user_input:
    user_message = prompt if prompt else user_input
    st.session_state["messages"].append({"role": "user", "content": user_message})

    # Query OpenAI API with the current messages
    with st.spinner("Generating response..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=st.session_state["messages"]
            )
            bot_reply = response.choices[0]["message"]["content"]
            st.session_state["messages"].append({"role": "assistant", "content": bot_reply})
        except Exception as e:
            bot_reply = f"Error retrieving response: {e}"
            st.session_state["messages"].append({"role": "assistant", "content": bot_reply})

# Display chat history sequentially
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])
