# OSC HACKATON PROJECT
💊 MediTracker Pro
MediTracker Pro is a Streamlit web application designed as a smart companion for managing your medication schedules, tracking adherence, and monitoring related health metrics like side effects and mood.


1. Features
Medication Scheduling: Add and track medications with customizable dosages, frequencies, and specific dose times.

Side Effect Logging: Easily report side effects with severity ratings (1-5) and link them to specific medications.

Data Management: Local data persistence (JSON) and an export feature to download your health data.


2. Prerequisites
You must have Python 3.7+ installed on your system.

3. Setup and Installation
Follow these steps to get MediTracker Pro running locally:

Save and Download the file
Since the code was provided as a file, ensure you have the app4.py file saved in a directory.

Install Dependencies:
The application relies on the following Python packages: streamlit, pandas, plotly-express, and plotly.
In your IDE terminal, type in "pip install" and then the package name. Example: pip install pandas.
Make sure to install all the packages or the application wont run. 

Run the application:
In order to run the applicatoin, type "streamlit run app4.py" into the terminal of your IDE. If you changed
the file name, replace app4.py with what you saved as in your device. 

Finally, a window should open up with the application running. 


Step 4: Usage


1. Dashboard 
Provides an overview of active medications, recent side effects, and archived meds.

Use the "⚠️ Report Side Effect" button for quick navigation to the Side Effects page.

2. Add Medication 
Fill in the Medication Name and Dosage.

Specify How many times per day and then set the exact Medication Times for each dose.

Click Add Medication to save.

3. Manage Medications 
Active Medications: View details, and choose to Archive (for temporary cessation) or Delete (permanently remove) a medication and its associated side effect logs. Note: Archiving requires selecting a reason.

Archived Medications: View past medications and choose to Reactivate or Delete permanently.

Bulk Actions: Contains database statistics and a button to Clean Old Data (removes side effect logs older than 1 year).

4. Side Effects 
Report Side Effect: Select the active medication, describe the Side Effect, rate its Severity, and add Additional Details.

Side Effect History: Displays the 10 most recent side effect reports.




