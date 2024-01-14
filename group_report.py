import os
import tools 
import argparse
from tools import load_config


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", '-c', type=str, default="./data/config.yaml")
    parser.add_argument('--name', '-n', type=str, required=True, help='群聊名称，注意不是群聊备注名')
    args = parser.parse_args()
    args = load_config(args)
    return args


if __name__ == "__main__":
    args = parse_args()
    contacts, messages = tools.load_data(args)
    group, fullname = tools.filter_by_name(messages, args.name)
    n_mess, n_char = tools.calculate_words(group)
    latest = tools.get_latest_time(group, args.latest_hour)
    cnt = tools.plot_wordcloud(group, os.path.join(args.output_dir, f"wc_{fullname}.png"))

    print(f"\n👏群聊【{fullname}】2023年度报告\n")
    print("📊这一年中，我们在群里一共发出了{}条消息，{}个字".format(n_mess, n_char))
    print("  其中最晚的一条消息是【{}】在【{}】发出的，内容是【{}】".format(
        latest["Sender"], latest["StrTime"], latest["StrContent"]))
    
    actives = tools.most_active_person_in_group(group)
    print("\n🙋‍♂️本群水群小能手排行：")
    print("  🥇【{}】产出了{}条消息， 共{}个字的废话".format(actives[0][0], actives[0][1], actives[0][2]))
    print("  🥈【{}】产出了{}条消息， 共{}个字的废话".format(actives[1][0], actives[1][1], actives[1][2]))
    print("  🥉【{}】产出了{}条消息， 共{}个字的废话".format(actives[2][0], actives[2][1], actives[2][2]))
    
    print("\n🔥本群年度热词Top5：")
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    for i in range(min(5, len(cnt))):
        print("{}【{}】共出现了{}次".format(emojis[i], cnt[i][0], cnt[i][1]))
    
    emojis = tools.top_emoji(group)
    print("\n🤚本群年度表情包Top5:")
    for i in range(min(5, len(emojis))):
        print("{}".format(emojis[i][0]), end=" ")
    
    tools.plot_nmess_per_minute(group, os.path.join(args.output_dir, f"nmess_per_minute_{fullname}.png"))    
    tools.plot_nmess_per_month(group, os.path.join(args.output_dir, f"nmess_per_month_{fullname}.png"))