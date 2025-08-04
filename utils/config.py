import os
from dotenv import load_dotenv

load_dotenv()  # Loading variables from .env automatic

def load_config():
    env = os.getenv('ENVIRONMENT', 'TEST').upper() # Use MAIN in main

    config = {
        'MAIN': {
            'token': os.getenv('MAIN_TOKEN'),
            'start_here_channel_id': int(os.getenv('START_HERE_ID', '1399070297365155850')),
            'welcome_channel_id': int(os.getenv('WELCOME_CHANNEL_ID', '825128605868490815')),
            'introduction_channel_id': int(os.getenv('INTRODUCTION_CHANNEL_ID', '1151609579000561776')),
            'information_channel_id': int(os.getenv('INFORMATION_CHANNEL_ID', '1363917217309130963')),
            'rules_channel_id': int(os.getenv('RULES_CHANNEL_ID', '1135973867001753711')),
            'help_channel_id': int(os.getenv('HELP_CHANNEL_ID', '1397028615446855780')),
        },
        'TEST': {
            'token': os.getenv('TEST_TOKEN'),
            'start_here_channel_id': int(os.getenv('TEST_START_HERE_ID', '1400948241683714148')),
            'welcome_channel_id': int(os.getenv('TEST_WELCOME_CHANNEL_ID', '676134286788788246')),
            'introduction_channel_id': int(os.getenv('TEST_INTRODUCTION_CHANNEL_ID', '1135933120865107968')),
            'information_channel_id': int(os.getenv('TEST_INFORMATION_CHANNEL_ID', '1135937853558358016')),
            'rules_channel_id': int(os.getenv('TEST_RULES_CHANNEL_ID', '1135945246849642677')),
            'help_channel_id': int(os.getenv('TEST_HELP_CHANNEL_ID', '1400948272809377822')),
        }
    }

    return {
        'environment': env,
        'prefix': os.getenv('BOT_PREFIX', '!'),
        **config.get(env, config['MAIN'])
    }