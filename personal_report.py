import os
import time
import tools 
import argparse
from tools import load_config


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="./data/config.yaml")
    args = parser.parse_args()
    args = load_config(args)
    return args


if __name__ == "__main__":
    args = parse_args()
    contacts, messages = tools.load_data(args)
    me = messages[messages['Sender'] == args.my_wechat_name]
    me = me.reset_index()
    n_mess, n_char = tools.calculate_words(me)
    latest = tools.get_latest_time(me, args.latest_hour)
    cnt = tools.plot_wordcloud(me, os.path.join(args.output_dir, "wc_me.png"))
    
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
        len(messages[(messages["NickName"] == private_cnt.index[0]) & (messages["Sender"] != args.my_wechat_name)])))

    print("\n🔥我的年度热词Top5：")
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    for i in range(min(5, len(cnt))):
        print("{}【{}】共使用{}次".format(emojis[i], cnt[i][0], cnt[i][1]))
    
    emojis = tools.top_emoji(me)
    print("\n🤚我的年度表情包Top5:")
    for i in range(min(5, len(emojis))):
        print("{}".format(emojis[i][0]), end=" ")
    
    tools.plot_nmess_per_minute(me, os.path.join(args.output_dir, "nmess_per_minute.png"))
    tools.plot_nmess_per_month(me, os.path.join(args.output_dir, "nmess_per_month.png"))
    
    print("\n\n")