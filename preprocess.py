import re
import pandas as pd
from emojis import unify_emoji

MY_WECHAT_NAME = "my_wechat_name"    # 用来替代聊天记录文件中的【我】

def parse_message(msg: str):
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


def load_info(contacts_file: str = 'contacts.csv', 
              messages_file: str = 'messages.csv',
              start_date: str = "2023-01-01",
              end_date: str = "2024-01-01"):
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
