import re
import pandas as pd
from .emojis import unify_emoji

MY_WECHAT_NAME = "my_wechat_name"    # 用来替代聊天记录文件中的【我】


def filter_group(df: pd.DataFrame, group_name: str):
    # 查找某个特定名称群聊的聊天记录
    res = df[df["NickName"].apply(lambda x: group_name in x)]
    fullname = res["NickName"].value_counts().index[0]
    filtered = res[res["NickName"] == fullname]
    filtered = filtered.reset_index()
    return filtered, fullname


def filter_friend(df: pd.DataFrame, friend_name: str):
    # 查找某个特定名称联系人的聊天记录
    res = df[df["NickName"].apply(lambda x: friend_name in x)]
    fullname = res["NickName"].value_counts().index[0]
    filtered = res[res["NickName"] == fullname]
    filtered = filtered.reset_index()
    return filtered, fullname


def parse_message(msg: str):
    # 过滤掉部份无用的消息: 表情包、语音、图片、视频、位置、名片、系统消息
    emoji_pattern = re.compile("<emoji .*?>")
    voice_pattern = re.compile("<voicemsg .*?/>")
    image_pattern = re.compile("<img .*?/>")
    video_pattern = re.compile("<videomsg .*?/>")
    location_pattern = re.compile("<location .*?")
    card_pattern = re.compile("<msg.*?username=.*?>")
    sys_pattern = re.compile("<a href=.*?</a>")
    
    for pattern in [emoji_pattern, voice_pattern, image_pattern, video_pattern, 
                    location_pattern, card_pattern, sys_pattern]:
        if pattern.search(msg) is not None:
            return False
    return True


def load_data(contacts_file: str = './data/contacts.csv', 
              messages_file: str = './data/messages.csv',
              start_date: str = "2023-01-01",
              end_date: str = "2024-01-01"):
    # 读取[start_date, end_date)时间段内的聊天记录(不包括end_date当天)
    global contacts, messages
    contacts = pd.read_csv(contacts_file, index_col=False)
    
    # 区分群聊和联系人
    isgroup = {}
    for i, row in contacts.iterrows():
        isgroup[row['NickName']] = 'chatroom' in row['UserName']
        
    # 将备注名转换为微信昵称
    remark2nickname = {'我': MY_WECHAT_NAME}
    for i, row in contacts.iterrows():
        if not isgroup[row['NickName']] and row['Remark']:
            remark2nickname[row['Remark']] = row['NickName']
        
    messages = pd.read_csv(messages_file, index_col=False)
    messages.dropna(subset=["StrContent", "NickName", "StrTime"], inplace=True)
    messages = messages[(messages["StrTime"] >= start_date) & \
                        (messages["StrTime"] < end_date) & \
                        (messages["StrContent"].apply(parse_message))]
    messages = messages[~messages['NickName'].isin(['微信团队', '腾讯客服'])]
    
    messages["isGroup"] = messages["NickName"].apply(lambda x: isgroup[x])
    messages["Sender"] = messages["Sender"].apply(lambda x: remark2nickname.get(x, x))
    messages.reset_index(inplace=True)
    
    messages["StrContent"] = messages["StrContent"].apply(unify_emoji)
    messages = messages[messages["Type"] == 1]
    
    return contacts, messages



if __name__ == "__main__":
    contacts, messages = load_info()
    print(messages.head())
