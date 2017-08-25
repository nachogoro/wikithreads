#!/usr/bin/env python

import twclient

import argparse
import re
import wikipedia


TWEET_LENGTH = 140
MINIMUM_SPLIT_LENGTH = 40
TWEET_LENGTH_IF_SHORT = TWEET_LENGTH - MINIMUM_SPLIT_LENGTH

IGNORED_SECTIONS = ('Véase también', 'Referencias',
                    'Enlaces externos', 'Bibliografía')


def clean_string(dirty):
    '''
    Removes all the references in a Wikipedia line
    '''
    dirty.replace(u'\u200b', '')
    return re.sub("\[[0-9]+\]", "", dirty).strip()


def split_text(text):
    '''
    Given a list of lines, split them in strings of less than 140 in a smart
    way: lines beginning with ## are treated as section titles and no resulting
    tweet should be too short.
    '''
    result = []

    for line in text:
        if not line:
            continue

        if line.startswith('##'):
            line = line[2:].upper()

        while line:
            end_of_tweet = len(line)
            if len(line) > TWEET_LENGTH:
                # Make it the last space
                end_of_tweet = line[:TWEET_LENGTH].rfind(' ')
                # If the remaining tweet would be too short, make the first one
                # shorter to balance it
                if len(line) - end_of_tweet < MINIMUM_SPLIT_LENGTH:
                    end_of_tweet = line[:TWEET_LENGTH_IF_SHORT].rfind(' ')

            result.append(line[:end_of_tweet])
            line = line[end_of_tweet+1:]

    return result


def main():
    parser = argparse.ArgumentParser(
        description='Toma un tema de la Wikipedia y lo twitea como hilo')
    parser.add_argument('-c',
                        action='store_true',
                        help='Loguearse como el último usuario utilizado')
    parser.add_argument('-s',
                        action='store_true',
                        help='Postear no solo el resumen de Wikipedia sino ' +
                        'también sus secciones')
    args = parser.parse_args()
    use_last_creds = args.c
    post_sections = args.s

    wikipedia.set_lang('es')

    name = input('¿De qué quieres tirarte el pisto?: ')
    search_results = wikipedia.search(name)

    if len(search_results) > 1:
        result_str = ''
        for i, e in enumerate(search_results):
            result_str += '[{}] {}\n'.format(i+1, e)

        print()
        option = input('Sé más preciso:\n' + result_str +
                       '\nNúmero de opción: ')
        page = wikipedia.page(search_results[int(option)-1])
    elif len(search_results) == 1:
        page = wikipedia.page(search_results[0])
    else:
        print('Lo siento, no hay nada para esa búsqueda :(')
        exit(0)

    # Store the page as a list of strings
    text = [u'No sé si conocéis {}. Abro hilo \U0001F447'.format(page.title)]

    text.extend([clean_string(i) for i in page.summary.splitlines()])

    if post_sections:
        for section in page.sections:
            if section in IGNORED_SECTIONS:
                continue

            text.append('##{}'.format(section))
            text.extend(
                [clean_string(i) for i in page.section(section).splitlines()])

    # Split text into tweets
    tweets = split_text(text)

    print()
    twclient.post_as_thread(tweets, use_last_creds)
    print('¡Enhorabuena!' +
          '¡Ahora todos piensan que eres un experto en {}!'.format(page.title))


if __name__ == '__main__':
    main()
