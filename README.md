# everlearn

This software generates revision questions and answers, in the form of
flashcards, based on a syllabus.  
In particular it can output the flashcards in the popular
[Anki](https://apps.ankiweb.net/) format, supported by many
flashcards apps available on mobile and desktop.

The questions, answers and images are generated automatically using AI
via LLMs.

The topics of the questions are chosen based on a syllabus that you
provide as a text file.
The content comes from within the language model.  By adjusting the
prompts in the system somewhat, one could make it extract questions from
content rather than a syllabus specifically. 

# Implementation
This code was written in a few hours during the 42 Hackathon in
London, February 2024.  Although usable, this code is rough. See it as
a demo of what is possibe.

# Requires
* Anthropic API key - for generating questions and answers
* OpenAI API key - for generating images
* Anki software for viewing the generated .apkg file.

# Instructions
Install the Python requirements (best inside a virtual environment).

```pip install -r requirements.txt```

Supply your API keys via shell environment variables.

```
export ANTHROPIC_API_KEY=YOUR_KEY_HERE
export OPENAI_API_KEY=YOUR_KEY_HERE
```

Supply a syllabus of study topic in the file syllabus.

Run the AI generation (takes a few minutes)

```python generate_cards.py```

This creates an .apkg file with Anki cards;
Load this into Anki.

# Example application: Geography revision
You can download a sample output file [directly from OneDrive](https://codemaestroai-my.sharepoint.com/:u:/g/personal/szummer_igent_ai/EVc8zoXatehNoTR6wE16TnwBbkWFYSTJJ-tdaOssCj8JlA?e=Ncg6cT).

View the .apkg flashcard deck in your favorite Anki app.  Install [here](https://apps.ankiweb.net/), for desktop and mobile platforms.

After starting the app, select 'Import' and specify the generated .apkg file.

# Cost of running this
The costs of creating questions and  is about $0.05 per card, as of early 2024.  The cost is currently dominated by the image generation.
