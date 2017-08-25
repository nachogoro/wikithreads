## About

Threadify is a tool to pretend you are an expert on topics you've never
bothered to research.

The way it works is that it asks you what topic you would like to 'research'.
It will then go to the Spanish Wikipedia and retrieve all the entries that
might be a match. You only need to chose which page to scrap, and it will
automatically convert it into a series of tweets and post them from your
Twitter account!

Since I had the Spanish audience in mind when I did it, the prompts on the
screen are in Spanish, sorry!

## Motivations

As people say in Galicia: "Para non saber falas abondo".

The number of people writing long Twitter threads on topics they only know
superficially at best is growing exponentially. The idea is that this tool will
free them from having to write those threads so that they can use that time
more productively (for example, actually researching the topic in depth).

## Requirements

The project is built with Python 3.5.2 in mind.
The libraries are specified in `requirements.txt`, and can be installed with:

`pip install -r requirements.txt`

(If you haven't heard of
[virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) don't put
it off any longer and learn about it now!).

You must have a Twitter account to log into (obviously).

Finally, you will need to register an application with Twitter at [Twitter
Application Management](https://apps.twitter.com/) in order to get your own
consumer key and consumer secret.

## Usage

First of all, modify `CONSUMER_KEY` and `CONSUMER_SECRET` inside `twclient.py`
to use your own (see [Requirements](#requirements)).

Then, simply run `./threadify.py`.

If option `-c`is specified, it will attempt to log into Twitter using the last
used account. If it fails to, it will prompt the user to authorize it
themselves.

If option `-s` is specified, it will tweet the different sections of the
Wikipedia article, not only the initial summary.
