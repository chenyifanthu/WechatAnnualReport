import time
import pandas as pd

from .emojis import EMOJI_PATTERN


def calculate_words(df: pd.DataFrame):
    n_mess = len(df)
    n_char = sum(df['StrContent'].apply(len))
    return n_mess, n_char
    
    
def get_latest_time(df: pd.DataFrame, latest_hour: float = 5.0):
    # 获取聊天记录中最晚的一条消息信息
    # latest_hour: 一天的最晚时间，超过这个时间的消息会被归到第二天 (Default: 5:00)
    def score(x):
        hour, min, sec = time.localtime(x)[3:6]
        if hour < latest_hour:
            hour += 24
        return hour * 3600 + min * 60 + sec

    late_score = df['CreateTime'].apply(score)
    latest = df.iloc[late_score.idxmax()]
    return latest


def most_active_person_in_group(df: pd.DataFrame, topk: int = 3):
    vc = df["Sender"].value_counts()
    name, n_mess = vc.index, vc.values
    results = []
    for i in range(topk):
        n_char = sum(df[df["Sender"] == name[i]]["StrContent"].apply(len))
        results.append((name[i], n_mess[i], n_char))
    return results


def most_active_day(df):
    ymd = df['CreateTime'].apply(lambda x: time.strftime("%Y-%m-%d", time.localtime(x)))
    days = ymd.value_counts()
    return days.value_counts().sort_index().idxmax()


def top_emoji(df: pd.DataFrame):
    cnt = {}
    for i, row in df.iterrows():
        res_all = EMOJI_PATTERN.findall(row["StrContent"])
        for res in res_all:
            if len(res) < 10:
                cnt[res] = cnt.get(res, 0) + 1
    cnt = sorted(cnt.items(), key=lambda x: x[1], reverse=True)
    return cnt