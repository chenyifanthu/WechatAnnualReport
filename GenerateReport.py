import re
import time
import tools 

import pandas as pd
import matplotlib.pyplot as plt

from tqdm import tqdm
from collections import Counter
from wordcloud import WordCloud, STOPWORDS






def personal_annual_report():
    global messages
    me = messages[messages['Sender'] == MY_WECHAT_NAME]
    me = me.reset_index()
    n_mess, n_char = tools.calculate_words(me)
    latest = tools.get_latest_time(me)
    cnt = tools.plot_wordcloud(me)
    
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
