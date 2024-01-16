"""
一个很有意思的模块，聊天记录摘要总结
选用了国内的ChatGLM模型api，有免费额度且稳定。
网址 https://open.bigmodel.cn/，注册送300w个免费token，基本够用了。
涉及到聊天记录云端处理，可以参考隐私政策：https://open.bigmodel.cn/dev/howuse/privacypolicy
功能还在测试中，还没集成到聊天记录报告里面，可以单独调试
"""

import zhipuai
import pandas as pd


zhipuai.api_key = ""

SUMMARIZE_GROUP_PROMPT = "你是一个聪明的群聊机器人。下面是某天的聊天记录，每行文本代表一条信息，冒号前的是发送者昵称，后面是发送内容。请对其进行自动摘要，你可以从聊天记录中分析这一天的讨论内容、不同人讨论的侧重点以及情感，你也可以猜测这一天发生了什么事，或者加入其它你认为有意思的一些分析。请直接返回生成的摘要内容文本，不超过800字，返回的文本请以“在这一天中”作为开头。\n%s"


def df2plaintext(df: pd.DataFrame) -> str:
    sender_content = df.apply(lambda x: f"{x['Sender']}: {x['StrContent']}", axis=1)
    final = "\n".join(sender_content)
    return final
    

def summarize_chat_history(df: pd.DataFrame,
                           prompt: str = SUMMARIZE_GROUP_PROMPT) -> str:
    """
    Summarize chat history using chatglm_turbo model.
    """
    plaintext = df2plaintext(df)
    print(plaintext)
    response = zhipuai.model_api.invoke(
        model = "chatglm_turbo",
        prompt = prompt % plaintext,
    )
    if response["success"]:
        ret = response["data"]["choices"][0]["content"]
        ret = ret.replace("\\n", "").replace("\"", "").strip()
        return ret
        
    else:
        return ""
    
    
if __name__ == "__main__":
    import sys; sys.path.append(".")
    import tools, argparse, time
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="./data/config.yaml")
    parser.add_argument('--name', '-n', type=str, required=True, help='群聊名称，注意不是群聊备注名')
    args = parser.parse_args()
    args = tools.load_config(args)
    contacts, messages = tools.load_data(args)
    group, fullname = tools.filter_by_name(messages, args.name)
    
    # 获取该群聊聊天最多的一天的聊天记录
    yymmdd = group["CreateTime"].apply(lambda x: time.strftime("%Y年%m月%d日", time.localtime(x)))
    top_day = yymmdd.value_counts().index[0]
    group_sel = group[yymmdd == top_day]
    group_sel.reset_index(inplace=True, drop=True)
    
    # 调用模型进行自动摘要
    summarize = summarize_chat_history(group_sel)
    print(summarize)
