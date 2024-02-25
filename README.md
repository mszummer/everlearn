# everlearn

This code is for using Generative AI for creating synthetic Anki Flash cards.
Based on a syllabus (input in the file syllabus.txt), the system automatically generates questions, answers, and images representative of the flash card.

This code was written in a few hours during the 42 London Hackathon. 

# Requires
* ANTHROPIC API key - for generating 
* OPEN API key - for generating images
* Anki software for viewing the generated .apkg file.

# Instructions
Install the Python requirements.
pip install -r requirements.txt

Supply your API keys in the shell:

export 
ANHTHROPIC_API_KEY=<YOUR_KEY_HERE_NO_SPACE_AROUND_EQUALS>
export OPENAI_API_KEY=<YOUR_KEY_HERE_NO_SPACE_AROUND_EQUALS>

Supply a syllabus of study topic in the file syllabus.txt

Run the AI generation (takes a few minutes)

python generate_cards.py

Load the output file: geography.apkg into Anki

# You can also download the geography.apkg file directly from here:

https://codemaestroai-my.sharepoint.com/:u:/g/personal/szummer_igent_ai/EVc8zoXatehNoTR6wE16TnwBbkWFYSTJJ-tdaOssCj8JlA?e=Ncg6cT
anki

View the .apkg flashcard deck in your favorite Anki app.  Install here:
Mac, iOS, Android etc:  https://apps.ankiweb.net/

After starting the app, select 'Import' and specify the generated .apkg file.