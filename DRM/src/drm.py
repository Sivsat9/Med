import os
import csv
import fnmatch
import openai

import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set up the OpenAI API key
openai.api_key = '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'

# Function to remove .txt files from a directory
def clean_directory(directory):
    # Check if directory exists
    if os.path.exists(directory):
        # Loop through all files in the directory
        for file in os.listdir(directory):
            # Check if the file ends with '.txt'
            if fnmatch.fnmatch(file, '*.txt'):
                file_path = os.path.join(directory, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {str(e)}")
    else:
        print(f"Directory {directory} not found")

# Function to read file content
def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Function to write response to a file
def write_file(file_path, content):
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w') as file:
        file.write(content)

# Function to create the directory if it doesn't exist
def create_output_folder():
    if not os.path.exists("../outputs/responses"):
        os.makedirs("../outputs/responses")

# Function to generate the text file for each patient
def create_patient_file(patient_data):
    # Replace spaces in patient name with underscores
    patient_name = patient_data['PATIENT_NAME']
    patient_name_file = patient_name.replace(" ", "_")  # Replace space with underscore
    
    file_name = f"../outputs/{patient_name_file}.txt"
    
    # Open the file and write the content
    with open(file_name, "w") as f:
        f.write(f"Patient Name: {patient_name}\n")
        f.write(f"1. Based on the medical history of patient {patient_name}, what lifestyle modifications (exercise and diet) can be recommended to reduce the risk of developing diabetes?\n")
        f.write(f"2. If exercise and diet can help manage blood sugar levels for patient {patient_name}, please provide specific recommendations, including:\n")
        f.write(f"    * Type of exercise: What forms of physical activity are most beneficial for improving insulin sensitivity?\n")
        f.write(f"    * Duration and frequency: How long and how often should patient {patient_name} engage in these exercises?\n")
        f.write(f"    * Dietary recommendations: What foods with a low glycemic index (GI) are recommended for maintaining healthy blood sugar levels?\n")
        f.write(f"        * For dietary support, can you provide three YouTube static link in the format: 'https://www.youtube.com/results?search_query=<search keywords>+{patient_data['LANGUAGE']}' for diabetic-friendly recipes with a focus on maintaining a low glycemic index?\n")
        f.write(f"3. Does patient {patient_name} require any of the following interventions to manage blood sugar levels:\n")
        f.write(f"    * HbA1c Testing: Would regular A1c monitoring be necessary for patient {patient_name} based on current risk factors?\n")
        f.write(f"    * Medications: Is there a need for oral hypoglycemic tablets to control blood sugar levels?\n")
        f.write(f"    * GLP-1 Agonists: Would patient {patient_name} benefit from GLP-1 receptor agonists to manage blood sugar levels and aid in weight management?\n")
        f.write(f"    * Insulin Therapy: Is insulin therapy required at this stage, or can patient {patient_name} continue with non-insulin interventions?\n\n")
        
        f.write(f"Patient’s AGE: {patient_data['AGE']}\n")
        f.write(f"BMI: {patient_data['BMI']}\n")
        f.write(f"HBA1C: {patient_data['HBA1C']}\n")
        f.write(f"Fasting Sugar: {patient_data['FASTING_SUGAR']}\n")
        f.write(f"Heredity Info: {patient_data['HEREDITY_INFO']}\n")

        f.write(f"Let the responses be as if Dr.GenAI to to {patient_name}\n")

# Main function to loop through all .txt files in ../outputs and generate a response
def process_files():
    conversation = []  # To store user and assistant messages

    # Loop through the files in the '../outputs' directory
    for file in os.listdir('../outputs'):
        # Check if the file ends with '.txt'
        if fnmatch.fnmatch(file, '*.txt'):
            # Append prefix path to file name
            file_name = os.path.join('../outputs', file)
            print(file_name)

            # Check if file exists
            if os.path.exists(file_name):
                # Read user input from the file
                user_input = read_file(file_name)
                conversation.append(
                    {
                        "role": "user",
                        "content": user_input
                    }
                )

                # Call OpenAI's GPT-4 model to get a response
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=conversation
                    )
                except Exception as e:
                    print(f"Error: {e}")
                    continue  # Skip to the next file if there's an error

                # Extract assistant's response
                assistant_response = response["choices"][0]["message"]["content"]
                conversation.append(
                    {
                        "role": "assistant",
                        "content": assistant_response
                    }
                )

                # Write the assistant's response to ../outputs/responses/<filename>
                write_file(f'../outputs/responses/{file}', assistant_response)

                print(f"\nFor file {file_name}:")
                print("\n" + assistant_response + "\n")
                print("======================================================\n")
            else:
                print(f"File {file_name} not found!")

# Email sending function
def send_email(to_email, subject, body):
    sender_email = "genaihospital@gmail.com"
    #password = os.getenv('EMAIL_PASSWORD')  # Use environment variable for security
    password = "tuoa hjol xjtc mwdu"  # Add your email password here

    # Setup the MIME
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    # Attach the email body
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Create the server object
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        
        # Send the email
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}. Error: {str(e)}")

# Main function to send personalized emails
def send_patient_emails(patient_data):
    for index, row in patient_data.iterrows():
        # Extract patient name and email
        full_name = row['PATIENT_NAME']
        email = row['EMAIL']
        
        # Split name to get first and last name
        name_parts = full_name.split()
        first_name = name_parts[0]
        last_name = name_parts[-1]
        
        # Construct the file path to the personalized response
        file_path = f"../outputs/responses/{first_name}_{last_name}.txt"
        
        # Try to read the personalized response file
        try:
            with open(file_path, 'r') as file:
                email_body = file.read()
        except FileNotFoundError:
            print(f"Response file not found for {full_name}")
            continue
        
        # Send the email
        send_email(email, f"Health Report for {full_name}", email_body)

# Main function to read the CSV file and generate the patient files
def main():
    create_output_folder()

    # Directories to clean
    output_dir = '../outputs/'
    responses_dir = '../outputs/responses/'

    # Clean both directories
    clean_directory(output_dir)
    clean_directory(responses_dir)
    
    input_file = "../inputs/Patient_Health_Records.csv"
    with open(input_file, mode="r", encoding="utf-8-sig") as file:
        csv_reader = csv.DictReader(file)
        
        # Skip the first row if it contains "PATIENT_NAME"
        for row in csv_reader:
            # If the 'PATIENT_NAME' field in the row is the column header, skip the row
            if row['PATIENT_NAME'] == "PATIENT_NAME":
                continue
            
            create_patient_file(row)

# Run the main function
if __name__ == "__main__":
    main()
    process_files()

    # Load patient data from the provided CSV
    file_path = '../inputs/Patient_Health_Records.csv'
    patient_data = pd.read_csv(file_path)
    send_patient_emails(patient_data)
