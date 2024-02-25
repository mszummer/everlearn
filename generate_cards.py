import re
import anthropic
import os
import json
import pickle
from openai import OpenAI
import genanki
import requests

system_prompt = """You are a very diligent student studying for your AS-level exam. 
Your level is that of a 17-year old.
To revise the material, you will soon be writing flash-cards with revision-questions for yourself. 

First, you carefully read the syllabus.  The syllabus is given next, in between <syllabus> </syllabus> tags.
"""

user_prompt_pre = """For this syllabus, think of what the most important concepts, facts and contexts are.

Then, think of how many flashcards are required to cover these: allocate a separate flashcard per important item.

For each flashcard, think of a visual images or worlds that are representative of its topic.
The images should be a typical, memorable and detailed.
Proceed to formulate questions, answers and descriptions of images for the flash-card, focusing on the concepts, contexts and topics you thought about. 
Write down your questions, answers and associated images, in the style of a flash-card.  
Use a succinct and information-rich style, to make review efficient.

For the image, write a extensive description of everything you see in the image:  
Describe the objects present, the background, colors, the textures, the style and mood. 

Write down each flashcard with your question, answer and image using tags as follows:
<flashcard>
<question>Flash card question.</question>
<answer>Flash card answer.</answer>
<image>Textual description of a flashcard image representative of the question topic.</image> 
</flashcard>

Repeat generating a flashcard for the remaining important items.

Skip preamble and boiler-plate in the response.
"""

from dataclasses import dataclass, asdict
import re

# Define the Card dataclass
@dataclass
class Card:
    question: str
    answer: str
    image_prompt: str
    image_url: str


def generate_image(prompt:str, client) -> str:
    """generate an image. Requires an OpenAI client"""
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1
    )
    image_url = response.data[0].url
    return image_url

def generate_images(cards:list[Card], client:str) -> None:
    """For each card, sets card.image_url to a newly generated image."""
    for card in cards:        
        card.image_url = generate_image(card.image_prompt, client)
        print(f'Generated: {card.image_url}\n')
        

def parse_questions(input_string: str) -> list[Card]:
    """
    Parses a string containing question and answer pairs in a custom XML format 
    and returns a list of Question objects.
    
    Parameters:
    - input_string: str. The input string in a custom XML format.
    
    Returns:
    - A list of Question objects extracted from the input string.
    """
    # Regular expression to find all question and answer pairs
    pattern = re.compile(r'<question>(.*?)<\/question>\s*<answer>(.*?)<\/answer>\s*<image>(.*?)<\/image>')
    
    # Find all matches of the pattern in the input string
    matches = pattern.findall(input_string)
    
    # Instantiate Question objects for each found pair and collect them in a list
    questions = [Card(question=match[0], answer=match[1], image_prompt=match[2], image_url="") for match in matches]
    
    return questions


def process(title: str, content: str, client, cards: list):
    global system_prompt
    global user_prompt_pre

    user_prompt = "Here is a syllabus: \n <syllabus>\n" + title + '\n' + content + "\n</syllabus>" + user_prompt_pre     
    message = client.messages.create(
        model="claude-2.1",
        max_tokens=2000,
        temperature=1,
        messages=[{"role": "system", 
                "content": system_prompt,
                "role": "user",
                "content": user_prompt
                }]    
        )
    text = message.content[0].text
    questions = parse_questions(text)
    # print(text)
    cards.extend(questions)


def remove_footer_and_process(filename, client):
    cards = []
    footer_text = "AQA AS Geography 7036. AS exams June 2017 onwards. Version 1.0 2 June 2016"
    # header_text = "Visit our website for information, guidance, support and resources at aqa.org.uk/7036"
    header_text = "Visit aqa.org.uk/7036 for the most up-to-date specification, resources, support and administration"
    
    with open(filename, 'r') as file:
        lines = file.readlines()
        
    # Filter out the footer text from each page
    lines = [line for line in lines if footer_text not in line and header_text not in line]
    
    section_pattern = re.compile(r'^\d+(\.\d+)*\s')
    current_section = ''
    section_content = []
    
    for line in lines:
        if section_pattern.match(line):
            # Output the previous section before starting a new one
            if current_section:
                print('Processing section: ' + current_section)
                process(current_section, ''.join(section_content), client, cards)
                section_content = []
            
            current_section = line.strip()
        else:
            if line.strip() != "":
               section_content.append(line)
    
    # Don't forget to output the last section
    if current_section:
        print('Processing section: ' + current_section)
        process(current_section, ''.join(section_content), client, cards)
    
    return cards

def pickle_cards(questions: list[Card], file_path: str) -> None:
    """Serialize a list of Question instances to a binary file."""
    with open(file_path, 'wb') as file:
        pickle.dump(questions, file)    
    print(f"Questions have been pickled and saved to: {file_path}")

def unpickle_cards(file_path: str) -> list[Card]:
    """Deserialize a list of Question instances from a binary file."""
    with open(file_path, 'rb') as file:
        questions = pickle.load(file)    
    return questions


def cards_to_jsonl(cards: list[Card], file_path: str) -> None:
    """Takes a list of Card instances, converts it to a JSON string, and saves the JSON string to a file."""
    try:
        # Convert the list of card instances to a list of dictionaries
        cards_dict = [asdict(card) for card in cards]
        
        # Convert the list of dictionaries to a JSON string
        json_output = json.dumps(cards_dict, indent=4)
        
        # Save the JSON string to the specified file
        with open(file_path, 'w') as f:
            f.write(json_output)
            
        print(f"cards exported to JSON and saved to file: {file_path}")
    except Exception as e:
        raise ValueError(f"Error exporting cards to JSON and saving to file: {e}")    
    

def cards_to_anki(card_list, deck_name='Geography', output_file='geography.apkg'):
    # Create a new Anki deck
    my_deck = genanki.Deck(
        deck_id=22222,  # Ensure this is a unique number
        name=deck_name,
    )

    # Define a model
    my_model = genanki.Model(
        model_id=33333,  # Ensure this is a unique number
        name='Simple Model with Image',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
            {'name': 'Image'},  # Field for images
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Question}}',  # How the question will be displayed
                'afmt': '{{FrontSide}}<br>{{Image}}<hr id="answer">{{Answer}}',  # How the answer will be displayed
            },
        ],
        css=""".card {
 font-family: arial;
 font-size: 20px;
 text-align: center;
 color: black;
 background-color: white;
}"""
    )

    # Helper function to possibly download/manage images, dummy for now
    def manage_image(image_url:str, image_name:str) -> None:
        # Here you might want to adjust the path or download the image if it's a URL
        # Send a GET request to the image URL
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(image_name, "wb") as file:
                file.write(response.content)
        else:
            print(f"Failed to download the image. Status code: {response.status_code}")

    # Add cards to the deck
    image_names=[]    
    for card in card_list:
        # Split the URL by '/' and get the last part, then split on ? to get the file name
        last_part = card.image_url.split('/')[-2]        
        image_name = last_part.split('?')[0]
        image_names.append(image_name)

        manage_image(card.image_url, image_name)  # Manage the image
        # my_image = card.image_url
        note = genanki.Note(
            model=my_model,
            fields=[card.question, card.answer, f'<img src="{image_name}">']
        )
        my_deck.add_note(note)

    # Use genanki's method to create a package
    my_package = genanki.Package(my_deck)
    my_package.media_files = image_names
    my_package.write_to_file(output_file)
    print('Saved: ' + output_file)        

def main():
    print(os.environ.get("ANTHROPIC_API_KEY"))    
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) 
    cards = remove_footer_and_process('syllabus.txt', client)
    pickle_cards(cards, "cards.pkl")
    cards_to_jsonl(cards, "cards.json")
    
    # For quick testing purposes, comment the above and uncomment the following two lines
    # cards = unpickle_cards("cards.pkl")  # can start from checkpoint
    # cards = cards[:1]    # for quick test runs
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    oai_client = OpenAI(api_key=OPENAI_API_KEY)
    generate_images(cards, oai_client)
    cards_to_anki(cards)

 
if __name__== "__main__":
    main()
