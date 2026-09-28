import os, re
templates_dir = r'c:\Users\dooli\OneDrive\Desktop\PYTHON-WEEKEND\templates'

def replace_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '#E5A700' not in content and 'bg-dark-yellow' not in content:
        return
        
    # We want to replace combinations of bg-dark-yellow and text-shield-navy
    # with bg-shield-blue and text-white.
    
    # First, let's remove the style block
    content = re.sub(r' style="background-color: #E5A700 !important; color: #16213e !important;"', '', content)
    content = re.sub(r' style="background-color: #E5A700 !important; width: (.*?);" ', r' style="width: \1;" ', content)
    content = re.sub(r' style="background-color: #E5A700 !important; width: (.*?);"', r' style="width: \1;"', content)
    content = re.sub(r' style="background-color: #E5A700 !important; color: #16213e !important; border: 2px solid #16213e !important; box-shadow: 2px 2px 0px #16213e !important;"', '', content)
    
    # Replace the classes
    # But wait! Some text-shield-navy might be somewhere else, so just simple replace:
    content = content.replace('text-shield-navy bg-dark-yellow', 'text-white bg-shield-blue')
    content = content.replace('bg-dark-yellow text-shield-navy', 'bg-shield-blue text-white')
    content = content.replace('bg-dark-yellow border-2.5', 'bg-shield-blue text-white border-2.5')
    content = content.replace('bg-dark-yellow border-1.5', 'bg-shield-blue text-white border-1.5')
    content = content.replace('bg-dark-yellow border-2', 'bg-shield-blue text-white border-2')
    content = content.replace('bg-dark-yellow', 'bg-shield-blue text-white')
    # clean up potential double text-white
    content = content.replace('text-white text-white', 'text-white')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

for root, _, files in os.walk(templates_dir):
    for file in files:
        if file.endswith('.html'):
            replace_in_file(os.path.join(root, file))
print('Done!')
