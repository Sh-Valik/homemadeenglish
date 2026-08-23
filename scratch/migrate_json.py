import json
import glob

def migrate_answers():
    files = glob.glob('content/topics/*.json')
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        modified = False
        
        # Migrate ru_to_en
        for ex in data.get('practice', {}).get('ru_to_en', []):
            if 'answer' in ex:
                ex['accepted_answers'] = [ex['answer']]
                del ex['answer']
                modified = True
                
        if modified:
            with open(f, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            print(f"Migrated {f}")

if __name__ == "__main__":
    migrate_answers()
