import subprocess
import yaml
from pathlib import Path
import time 
import random
import string
import re

def create_new_ai(ai_id):
    dir_path = f"ais/{ai_id}"
    
    subprocess.run(["mkdir", "-p", dir_path])
    subprocess.run(["cp", "-r", "template", dir_path])

def clear_existing_rasa_files(ai_id):
    dir_path = f"ais/{ai_id}"

    subprocess.run(["rm", "-f", "domain.yml", "data/nlu.yml", "data/stories.yml", "data/rules.yml"], 
                  cwd=dir_path)

def train_ai(ai_id):
    dir_path = f"ais/ai_id"

    subprocess.run(
        ["rasa", "train"],
        cwd=dir_path,  
        check=True
    )

def run_ai(ai_id):
    dir_path = f"ais/ai_id"
    
    subprocess.run(
        ["rasa", "shell"],
        cwd=dir_path,  
        check=True
    )

def create_domain_file(dir_path, json_data):
    slots_dict = {}
    for slot in json_data.get("slots", []):
        slots_dict[slot] = {
            "type": "text",
            "influence_conversation": True,
            "mappings": [{"type": "from_entity", "entity": slot}]
        }
    
    responses = {}
    for utterance in json_data.get("utterances", []):
        response_name = f"utter_{utterance['name']}"
        responses[response_name] = [{"text": utterance['text']}]
    
    forms = {}
    for form in json_data.get("forms", []):
        forms[form['name']] = {
            "required_slots": form.get('requiredSlots', [])
        }
    
    intents = [intent['name'] for intent in json_data.get("intents", [])]
    
    entities = []
    for intent in json_data.get("intents", []):
        for placeholder, entity in intent.get('slotMappings', {}).items():
            if entity not in entities:
                entities.append(entity)
    
    domain_content = {
        "version": "3.1",
        "intents": intents,
        "entities": entities,
        "slots": slots_dict,
        "responses": responses,
        "forms": forms
    }
    
    domain_path = Path(dir_path) / "domain.yml"
    with open(domain_path, "w") as f:
        yaml.dump(domain_content, f, sort_keys=False, default_flow_style=False)

def create_nlu_file(dir_path: Path, json_data: dict):
    nlu_data = []
    
    for intent in json_data.get("intents", []):
        if intent.get('examples'):
            nlu_data.append({
                "intent": intent['name'],
                "examples": "\n".join(f"- {ex}" for ex in intent['examples'])
            })
    
    nlu_content = {
        "version": "3.1",
        "nlu": nlu_data
    }
    
    nlu_path = Path(dir_path) / "data" / "nlu.yml"
    nlu_path.parent.mkdir(parents=True, exist_ok=True)
    with open(nlu_path, "w") as f:
        yaml.dump(nlu_content, f, sort_keys=False, default_flow_style=False, width=1000)

def create_stories_file(dir_path: Path, json_data: dict):
    stories_data = []
    
    for story in json_data.get("stories", []):
        story_steps = []
        for step in story.get('steps', []):
            if step['type'] == 'intent':
                story_steps.append({"intent": step['value']})
            elif step['type'] == 'action':
                story_steps.append({"action": step['value']})
            elif step['type'] == 'slot':
                story_steps.append({"slot_was_set": [{step.get('slot', 'slot_name'): step['value']}]})
        
        if story_steps:
            stories_data.append({
                "story": story['name'],
                "steps": story_steps
            })
    
    stories_content = {
        "version": "3.1",
        "stories": stories_data
    }
    
    stories_path = Path(dir_path) / "data" / "stories.yml"
    stories_path.parent.mkdir(parents=True, exist_ok=True)
    with open(stories_path, "w") as f:
        yaml.dump(stories_content, f, sort_keys=False, default_flow_style=False)

def create_rules_file(dir_path: Path, json_data: dict):
    rules_data = []
    
    for mapping in json_data.get("mappings", []):
        rule_steps = [{"intent": mapping['intent']}]
        
        if mapping['type'] == 'response' and mapping.get('response'):
            rule_steps.append({"action": f"utter_{mapping['response']}"})
        elif mapping['type'] == 'form' and mapping.get('form'):
            rule_steps.append({"action": f"{mapping['form']}_form"})
        
        rules_data.append({
            "rule": f"Rule for {mapping['intent']}",
            "steps": rule_steps
        })
    
    for form in json_data.get("forms", []):
        rules_data.append({
            "rule": f"Activate {form['name']} form",
            "steps": [
                {"intent": f"request_{form['name']}"},
                {"action": f"{form['name']}_form"},
                {"active_loop": f"{form['name']}_form"}
            ]
        })
        
        rules_data.append({
            "rule": f"Submit {form['name']} form",
            "condition": [{"active_loop": f"{form['name']}_form"}],
            "steps": [
                {"action": f"{form['name']}_form"},
                {"active_loop": None},
                {"slot_was_set": [{"requested_slot": None}]},
                {"action": f"utter_{form['name']}_submit"}
            ]
        })
    
    rules_content = {
        "version": "3.1",
        "rules": rules_data
    }
    
    rules_path = Path(dir_path) / "data" / "rules.yml"
    rules_path.parent.mkdir(parents=True, exist_ok=True)
    with open(rules_path, "w") as f:
        yaml.dump(rules_content, f, sort_keys=False, default_flow_style=False)

def clear_existing_rasa_files(dir_path):
    files_to_clear = [
        Path(dir_path) / "domain.yml",
        Path(dir_path) / "data" / "nlu.yml",
        Path(dir_path) / "data" / "stories.yml",
        Path(dir_path) / "data" / "rules.yml"
    ]
    
    for file_path in files_to_clear:
        if file_path.exists():
            file_path.unlink()

def convert_json_to_rasa_ai(output_dir, json_data):
    dir_path = Path(output_dir)
    data_dir = dir_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    clear_existing_rasa_files(dir_path)
    
    create_domain_file(dir_path, json_data)
    create_nlu_file(dir_path, json_data)
    create_stories_file(dir_path, json_data)
    create_rules_file(dir_path, json_data)
    
    print(f"Successfully converted JSON to Rasa files in {dir_path}")

def generate_unique_chatbot_id(chatbot_name, base_dir="ais"):
    clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', chatbot_name)
    clean_name = clean_name.lower().replace(' ', '_')
    
    if not clean_name:
        clean_name = "chatbot"

    def generate_suffix(length=8):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def id_exists(chatbot_id):
        return Path(base_dir, chatbot_id).exists()
    
    def generate_chatbot_id ():
        return f"{clean_name}_{int(time.time())}_{generate_suffix()}"

    chatbot_id = generate_chatbot_id()
    while id_exists(chatbot_id):
        chatbot_id = generate_chatbot_id() 

    return chatbot_id

def create_chatbot(json_data):
    chatbot_name = json_data.get('name')
    chatbot_id = generate_unique_chatbot_id(chatbot_name)
    chatbot_path = f"ais/{chatbot_id}"

    convert_json_to_rasa_ai(chatbot_path, json_data)
