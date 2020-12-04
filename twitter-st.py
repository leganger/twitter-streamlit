import streamlit as st
import snscrape.modules.twitter as sntwitter
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from wordcloud import WordCloud

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


st.sidebar.title("Norsk Twitterbarometer")

keyword = st.sidebar.text_input("Søkeord")
from_date = st.sidebar.date_input("Fra dato", value=datetime.now()-timedelta(days=30), max_value=datetime.now())
to_date = st.sidebar.date_input("Til dato", value=datetime.now(), max_value=datetime.now())
max_num = st.sidebar.number_input("Maks antall tweets", value=100, min_value=0, max_value=5000)
search_button = st.sidebar.button("Analyser!")



if search_button:

    with st.spinner("Analyserer norske tweets..."):

        progress_bar = st.progress(0.0)

        # Scrape tweets
        scrape_string = '{keyword} lang:no since:{from_date} until:{to_date}'.format(
            keyword=keyword,
            from_date = from_date.strftime("%Y-%m-%d"),
            to_date = to_date.strftime("%Y-%m-%d")
        )

        tweets = []
        tweet_texts = ""
        for i,tweet in enumerate(sntwitter.TwitterSearchScraper(scrape_string).get_items()):
            if i>max_num:
                progress_bar.empty()
                break
            tweets.append([tweet.date, tweet.content, tweet.user.username])
            tweet_texts += tweet.content.lower()+" "
            progress_bar.progress(i/max_num)

        progress_bar.empty()

        # Create a wordcloud
        with open("stopwords_no.txt","r") as infile:
            stopwords = set(line.strip() for line in infile) 
        stopwords.update([keyword, keyword.replace("_"," "), keyword.replace(" ","_")])

        wordcloud = WordCloud(width=1500, height=1000, stopwords=stopwords, min_word_length=3, background_color="white").generate(tweet_texts)

        # Display the generated image:
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)

        # Create a dataframe from the tweets list above 
        tweets_df = pd.DataFrame(tweets, columns=['Datetime', 'Text', 'Username'])
        st.dataframe(tweets_df)