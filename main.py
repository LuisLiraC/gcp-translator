import os
import re
from google.cloud import translate_v2 as translate

os.environ['GOOGLE_APPLICATION_CREDENTIALS']='./gcp/credentials.json'
GOOGLE_API_MAX_LENGTH = 10000

# Files paths
VTT_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'vtt_files')
SRT_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'srt_files')
INPUT_FILES = os.listdir(VTT_PATH)

# Regex
MINUTE_LINE = re.compile(r'^[\d\.:]+ --> [\d\.:]+')
MINUTE = re.compile(r'([\d\.:]+) --> ([\d\.:]+)')
TEXT_LINE = re.compile(r'^[\w\"\'¿].*$')

def vttmin_to_srtmin(minute_list):
    srt_minute_list = []
    for line in minute_list:
        minutes = re.match(MINUTE, line)
        if not minutes:
            print(line)
        start_minute = '00:' + minutes.group(1).replace('.', ',')
        final_minute = '00:' + minutes.group(2).replace('.', ',')
        srt_line = start_minute + ' --> ' + final_minute
        srt_minute_list.append(srt_line)
    return srt_minute_list

def write_srt_file(output_file, minute_list, text_list):    
    with open(os.path.join(SRT_PATH, output_file), 'w', encoding='utf-8') as srt:
        for i in range(len(minute_list)):
            srt.write(f'{i + 1}')
            srt.write('\n')
            srt.write(minute_list[i])
            srt.write('\n')
            srt.write(text_list[i])
            srt.write('\n')
            if i != len(minute_list) - 1:
                srt.write('\n')
    print(f'Archivo {output_file} escrito satisfactoriamente ;)')

def chunk_list(some_list, n_chunks):
    wrapper_list = []
    general_chunk_size = len(some_list) // n_chunks
    general_chunk_size = general_chunk_size if general_chunk_size > 1 else 1
    index_accumulator_initial = 0
    index_accumulator_final = general_chunk_size
    while True: 
        if index_accumulator_final > len(some_list):
            return wrapper_list
        wrapper_list.append(some_list[index_accumulator_initial:index_accumulator_final])
        index_accumulator_initial, index_accumulator_final = index_accumulator_final, index_accumulator_final + general_chunk_size

def translate_text_list(text_list, option):
    translate_client = translate.Client()
    translated_text_list_raw = []

    if (option == 1):
        translated_text_list_raw = translate_client.translate(text_list, source_language='en', target_language='es')
    elif (option == 2):
        translated_text_list_raw = translate_client.translate(text_list, source_language='en', target_language='pt')
    elif (option == 3):
        translated_text_list_raw = translate_client.translate(text_list, source_language='es', target_language='en')
    elif (option == 4):
        translated_text_list_raw = translate_client.translate(text_list, source_language='es', target_language='pt')
    elif (option == 5):
        translated_text_list_raw = translate_client.translate(text_list, source_language='pt', target_language='en')
    elif (option == 6):
        translated_text_list_raw = translate_client.translate(text_list, source_language='pt', target_language='es')

    translated_text_list = []
    for line in translated_text_list_raw:
        translated_text_list.append(line['translatedText'])
    return translated_text_list


def run(option):
    for input_file in INPUT_FILES:
        minute_list = []
        text_list = []

        with open(os.path.join(VTT_PATH, input_file), 'r', encoding='utf-8') as vtt:
            for line in vtt:
                if line.strip() == "WEBVTT":
                    continue
                elif re.match(MINUTE_LINE, line):
                    minute_list.append(line.strip())
                elif re.match(TEXT_LINE, line):
                    text_list.append(line.strip())

        text_size = len(''.join(text_list))

        if text_size > GOOGLE_API_MAX_LENGTH: 
            qty_divisions = text_size // GOOGLE_API_MAX_LENGTH + 1
            translated_text_list = []
            for chunk in chunk_list(text_list, qty_divisions):
                chunk = translate_text_list(chunk, option)
                translated_text_list += chunk
        else:
            translated_text_list = translate_text_list(text_list, option)

        srt_minute_list = vttmin_to_srtmin(minute_list)

        input_language = None
        output_language = None

        if (option == 1):
            input_language = '_en.srt'
            output_language = '_es.srt'
        elif (option == 2):
            input_language = '_en.srt'
            output_language = '_pt.srt'
        elif (option == 3):
            input_language = '_es.srt'
            output_language = '_en.srt'
        elif (option == 4):
            input_language = '_es.srt'
            output_language = '_pt.srt'
        elif (option == 5):
            input_language = '_pt.srt'
            output_language = '_en.srt'
        elif (option == 6):
            input_language = '_pt.srt'
            output_language = '_es.srt'

        output_file_one = re.match(r'\w+', input_file).group(0) + input_language
        output_file_two = re.match(r'\w+', input_file).group(0) + output_language

        write_srt_file(output_file_one, srt_minute_list, text_list)
        write_srt_file(output_file_two, srt_minute_list, translated_text_list)


if __name__ == "__main__":
    option = 0
    while True:
        print("""
        Select an option:
        1. English to Spanish
        2. English to Portuguese
        3. Spanish to English
        4. Spanish to Portuguese
        5. Portuguese to English
        6. Portuguese to Spanish
        """)
        option = int(input())
        if (option > 0 and option < 7):
            break

    run(option)