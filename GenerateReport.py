import re
import time
import jieba 

import pandas as pd
import matplotlib.pyplot as plt

from tqdm import tqdm
from collections import Counter
from wordcloud import WordCloud, STOPWORDS
from preprocess import load_info, MY_WECHAT_NAME
from emojis import EMOJIS, EMOJI_PATTERN



def filter_group(df: pd.DataFrame, group_name: str):
    res = df[df["NickName"].apply(lambda x: group_name in x)]
    fullname = res["NickName"].value_counts().index[0]
    filtered = res[res["NickName"] == fullname]
    filtered = filtered.reset_index()
    return filtered, fullname

def filter_friend(df: pd.DataFrame, friend_name: str):
    res = df[df["NickName"].apply(lambda x: friend_name in x)]
    fullname = res["NickName"].value_counts().index[0]
    filtered = res[res["NickName"] == fullname]
    filtered = filtered.reset_index()
    return filtered, fullname


def calculate_words(df: pd.DataFrame):
    n_mess = len(df)
    n_char = sum(df['StrContent'].apply(len))
    return n_mess, n_char
    
    
def get_latest_time(df: pd.DataFrame, latest_hour: float = 5):
    def score(x):
        hour, min, sec = time.localtime(x)[3:6]
        if hour < latest_hour:
            hour += 24
        return hour * 3600 + min * 60 + sec

    late_score = df['CreateTime'].apply(score)
    latest = df.iloc[late_score.idxmax()]
    return latest


def plot_nmess_per_minute(df: pd.DataFrame):
    hours = df.CreateTime.apply(lambda x: int(time.strftime("%H", time.localtime(x))))
    minutes = df.CreateTime.apply(lambda x: int(time.strftime("%M", time.localtime(x))))
    df["time"] = hours * 60 + minutes
        
    plt.figure(figsize=(12, 4))
    df["time"].plot.hist(bins=1440, alpha=0.5)
    plt.title("Distribution of messages per minute")
    plt.xticks(range(0, 1440, 60), [str(i) for i in range(24)])
    plt.savefig("nmess_per_minute.png")
    
    
def plot_nmess_per_month(df: pd.DataFrame):
    months = df.CreateTime.apply(lambda x: int(time.strftime("%m", time.localtime(x))))
    plt.figure(figsize=(12, 4))
    months.value_counts().sort_index().plot.bar()
    plt.title("Distribution of messages per month")
    plt.savefig("nmess_per_month.png")


def plot_wordcloud(df, output_file: str = "wordcloud.png"):
    global STOPWORDS
    my_stopwords = open("stopwords.txt", "r", encoding="utf-8").read().split("\n")
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
    wc = WordCloud(font_path="simhei.ttf", background_color="white", max_words=2000,
                   stopwords=STOPWORDS, max_font_size=200, min_font_size=6,
                   width=1080, height=720, random_state=42,
                   repeat=False, collocations=False, )
    wc.generate(text)
    plt.figure(figsize=(12, 12))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(output_file)
    return cnt
    
    
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


def personal_annual_report():
    global messages
    me = messages[messages['Sender'] == MY_WECHAT_NAME]
    me = me.reset_index()
    n_mess, n_char = calculate_words(me)
    latest = get_latest_time(me)
    cnt = plot_wordcloud(me)
    
    print(f"\n👏个人微信2023年度报告\n")
    print("📊这一年中我总共给{}个群聊和{}个联系人发了{}条消息，共计{}个字。".format(
        len(me[me["isGroup"] == True]["NickName"].unique()), 
        len(me[me["isGroup"] == False]["NickName"].unique()), 
        n_mess, n_char), end="")
    to = "群聊" if latest["isGroup"] else "联系人"
    print("其中最晚的一条消息是在【{}】发给{}「{}」的，内容是「{}」\n".format(
        latest["StrTime"], to, latest["NickName"], latest["StrContent"]))
    
    day_cnt = me["CreateTime"].apply(lambda x: time.strftime("%Y年%m月%d日", time.localtime(x))).value_counts()
    print("\n📅【{}】这一天一定很特别，我疯狂发送了{}条微信。相比之下【{}】就显得很安静，只发了{}条消息。\n".format(
        day_cnt.index[0], day_cnt.values[0], day_cnt.index[-1], day_cnt.values[-1]))
    
    group_cnt = me[me["isGroup"] == True]["NickName"].value_counts()
    private_cnt = me[me["isGroup"] == False]["NickName"].value_counts()
    print("👉我最喜欢在群聊【{}】发言，贡献了{}条没什么价值的聊天记录。".format(
        group_cnt.index[0], group_cnt.values[0]))
    print("👉我最喜欢和联系人【{}】聊天，向ta激情发出{}条信息，得到了{}条回复。\n".format(
        private_cnt.index[0], private_cnt.values[0], 
        len(messages[(messages["NickName"] == private_cnt.index[0]) & (messages["Sender"] != MY_WECHAT_NAME)])))

    print("\n🔥我的年度热词Top5：")
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    for i in range(min(5, len(cnt))):
        print("{}【{}】共使用{}次".format(emojis[i], cnt[i][0], cnt[i][1]))
    
    emojis = top_emoji(me)
    print("\n🤚我的年度表情包Top5:")
    for i in range(min(5, len(emojis))):
        print("{}".format(emojis[i][0]), end=" ")
    
    plot_nmess_per_minute(me)
    plot_nmess_per_month(me)
    
    print("\n\n")


def group_chat_annual_report(groupname):
    global messages
    group, fullname = filter_group(messages, groupname)
    n_mess, n_char = calculate_words(group)
    latest = get_latest_time(group)
    cnt = plot_wordcloud(group)
    print(len(cnt[0][0]), cnt[0][0])
    print(f"\n👏群聊【{fullname}】2023年度报告\n")
    print("📊这一年中，我们在群里一共发出了{}条消息，{}个字".format(n_mess, n_char))
    print("  其中最晚的一条消息是【{}】在【{}】发出的，内容是【{}】".format(
        latest["Sender"], latest["StrTime"], latest["StrContent"]))
    
    actives = most_active_person_in_group(group)
    print("\n🙋‍♂️本群水群小能手排行：")
    print("  🥇【{}】产出了{}条消息， 共{}个字的废话".format(actives[0][0], actives[0][1], actives[0][2]))
    print("  🥈【{}】产出了{}条消息， 共{}个字的废话".format(actives[1][0], actives[1][1], actives[1][2]))
    print("  🥉【{}】产出了{}条消息， 共{}个字的废话".format(actives[2][0], actives[2][1], actives[2][2]))
    
    print("\n🔥本群年度热词Top5：")
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    for i in range(min(5, len(cnt))):
        print("{}【{}】共出现了{}次".format(emojis[i], cnt[i][0], cnt[i][1]))
    
    emojis = top_emoji(group)
    print("\n🤚本群年度表情包Top5:")
    for i in range(min(5, len(emojis))):
        print("{}".format(emojis[i][0]), end=" ")
    
    plot_nmess_per_minute(group)    
    plot_nmess_per_month(group)
    
    
def name2remark(name: str):
    global contacts
    if name == MY_WECHAT_NAME:
        return "我"
    res = contacts[contacts["NickName"] == name]["Remark"].values
    return res[0] if len(res) > 0 else name


def private_chat_annual_report(name):
    global messages
    friend, fullname = filter_friend(messages, name)
    n_mess, n_char = calculate_words(friend)
    latest = get_latest_time(friend)
    cnt = plot_wordcloud(friend)
    me = friend[friend['Sender'] == MY_WECHAT_NAME]
    me = me.reset_index(drop=True)
    cnt_me = plot_wordcloud(me, "wordcloud_me.png")
    ta = friend[friend['Sender'] == fullname]
    ta = ta.reset_index(drop=True)
    cnt_ta = plot_wordcloud(ta, "wordcloud_ta.png")
    print(f"\n👏你和【{fullname}】2023年度报告\n")
    print("📊这一年中，你们一共发出了{}条消息，{}个字".format(n_mess, n_char))
    print("  其中最晚的一条消息是【{}】在【{}】发出的，内容是【{}】".format(
        name2remark(latest["Sender"]), latest["StrTime"], latest["StrContent"]))
    
    print("\n🔥你们的年度热词Top5：")
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    for i in range(min(5, len(cnt))):
        print("{}【{}】共出现了{}次".format(emojis[i], cnt[i][0], cnt[i][1]))
    
    emojis = top_emoji(friend)
    print("\n🤚你们的年度表情包Top5:")
    for i in range(min(5, len(emojis))):
        print("{}".format(emojis[i][0]), end=" ")
        
    print("\n\n🔥我的年度热词Top5：")
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    for i in range(min(5, len(cnt_me))):
        print("{}【{}】共使用{}次".format(emojis[i], cnt_me[i][0], cnt_me[i][1]))
    
    emojis = top_emoji(me)
    print("\n🤚我的年度表情包Top5:")
    for i in range(min(5, len(emojis))):
        print("{}".format(emojis[i][0]), end=" ")
    
    print("\n\n🔥TA的年度热词Top5：")
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    for i in range(min(5, len(cnt_ta))):
        print("{}【{}】共使用{}次".format(emojis[i], cnt_ta[i][0], cnt_ta[i][1]))
    
    emojis = top_emoji(ta)
    print("\n🤚TA的年度表情包Top5:")
    for i in range(min(5, len(emojis))):
        print("{}".format(emojis[i][0]), end=" ")
    
    
    plot_nmess_per_minute(friend)    
    plot_nmess_per_month(friend)
    
    
    
    
if __name__ == "__main__":
    contacts, messages = load_info()
    personal_annual_report()
