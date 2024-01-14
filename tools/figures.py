import os
import time
import jieba 
import logging

import pandas as pd
import matplotlib.pyplot as plt

from tqdm import tqdm
from collections import Counter
from wordcloud import WordCloud, STOPWORDS
from .emojis import EMOJIS


def plot_nmess_per_minute(df: pd.DataFrame, output_file: str = "nmess_per_minute.png"):
    hours = df.CreateTime.apply(lambda x: int(time.strftime("%H", time.localtime(x))))
    minutes = df.CreateTime.apply(lambda x: int(time.strftime("%M", time.localtime(x))))
    df["time"] = hours * 60 + minutes
        
    plt.figure(figsize=(12, 4))
    df["time"].plot.hist(bins=1440, alpha=0.5)
    plt.title("Distribution of messages per minute")
    plt.xticks(range(0, 1440, 60), [str(i) for i in range(24)])
    plt.savefig(output_file)
    
    
    
def plot_nmess_per_month(df: pd.DataFrame, output_file: str = "nmess_per_minute.png"):
    months = df.CreateTime.apply(lambda x: int(time.strftime("%m", time.localtime(x))))
    plt.figure(figsize=(12, 4))
    months.value_counts().sort_index().plot.bar()
    plt.title("Distribution of messages per month")
    plt.savefig(output_file)



def plot_wordcloud(df: pd.DataFrame, output_file: str = "wordcloud.png"):
    global STOPWORDS
    jieba.setLogLevel(logging.INFO)
    
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))
    my_stopwords = open("data/stopwords.txt", "r", encoding="utf-8").read().split("\n")
    STOPWORDS |= set(my_stopwords + ["\r\n"])
    
    all_words = []
    for i, row in tqdm(df.iterrows(), total=len(df)):
        row_content = row["StrContent"]
        for emoji in EMOJIS:
            row_content = row_content.replace(emoji, " ")
        words = jieba.lcut(row_content)
        for word in words:
            if len(word) > 1 and word not in STOPWORDS:
                all_words.append(word)
                
    cnt = sorted(Counter(all_words).items(), key=lambda x: x[1], reverse=True)
    text = " ".join(all_words)
    wc = WordCloud(font_path="data/simhei.ttf", background_color="white", max_words=2000,
                   stopwords=STOPWORDS, max_font_size=200, min_font_size=6,
                   width=1080, height=720, random_state=42,
                   repeat=False, collocations=False, )
    wc.generate(text)
    plt.figure(figsize=(12, 12))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(output_file)
    return cnt