# This example requires the 'message_content' intent.
import os
from dotenv import load_dotenv
import discord

# .envファイルの内容を読み込見込む
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


flag = 0
round = 0
members = []
scores = []
records = [{"id":1, "scores":[]},{"id":2, "scores":[]},{"id":3, "scores":[]},{"id":4, "scores":[]}]

condition = True
@client.event
async def on_message(message):
    global flag, round, members, scores, records
    if message.author == client.user:
        return

    if message.content.startswith('hearts!start'):
        flag = 0

    match flag:
        #ゲーム開始
        case 0:
            if message.content.startswith('hearts!start'):
                await message.channel.send(
                    "Let's play hearts!!!\nゲームに参加する人は「hearts!member」と送信してください。\n参加者が4名集まり次第、ゲームが開始されます。"
                )
                flag = 1
                return

        #メンバー登録
        case 1:
            if message.content.startswith('hearts!member'):
                if message.author in members:
                    await message.channel.send(" <@{}> さんは既に参加登録されています。".format(message.author.id))
                    return
                members.append(message.author.id)
                cnt_members = len(members)
                if cnt_members < 4:
                    await message.channel.send(" <@{}> さんが参加登録されました。\n残りn名です。".format(message.author.id))
                    return
                elif cnt_members == 4:
                    for i,member in enumerate(members):
                        records[i]['id'] = member
                    await message.channel.send(" <@{}> さんが参加登録されました。\nゲームを開始します。".format(message.author.id))
                    await message.channel.send(
                        "---\n【ラウンド1】\nラウンド終了次第、自分のスコア(0~26)を送信してください。"
                    )
                    flag = 2
                    return
                else:
                    await message.channel.send("問題が発生しました。ゲームを強制終了します。")
                    flag = 0
                    members = []
                    return

        #ラウンド終了
        case 2:
            #ゲームに参加していないユーザーの場合
            if not message.author.id in members:
                await message.channel.send(" <@{}> さんは今回のゲームに参加していません。".format(message.author.id))
                return
            #整数ではない場合
            if not is_int(message.content):
                await message.channel.send(" <@{}> さん、0~26の整数を入力してください。".format(message.author.id))
                return
            #0~26の範囲ではない場合
            score = int(message.content, 10)
            if score < 0 or 26 < score:
                await message.channel.send(" <@{}> さん、0~26の整数を入力してください。".format(message.author.id))
                return
            
            #正常な入力
            scores.append(score)
            for i,record in enumerate(records):
                if record['id'] == message.author.id:
                    personal_cnt_scores = len(records[i]['scores'])
                    if personal_cnt_scores == round:
                        records[i]['scores'].append(score)
                    else:
                        records[i]['scores'][round] = score
            round_cnt_scores = len(scores)
            if round_cnt_scores < 4:
                return
            elif round_cnt_scores == 4:
                round_sum_score = sum(scores)
                #4名の合計点数が26点にならない場合
                if round_sum_score != 26:
                    await message.channel.send("スコア入力に誤りがあります。再度全員スコアを申告してください。")
                    scores = []
                    return
                #誰かの点数がマイナス100点を超えた
                for i, record in enumerate(records):
                    personal_sum_score = sum(record['scores'])
                    await message.channel.send(" <@{}> さんの合計スコアは{}点です。".format(record['id'], personal_sum_score))
                    if personal_sum_score >= 100:
                        flag = 3
            
            #ラウンド継続判断
            round += 1
            scores = []
            if flag == 2:
                await message.channel.send(
                    "---\n【ラウンド{}】\nラウンド終了次第、自分のスコア(0~26)を送信してください。".format(round+1)
                )
                return
            elif flag == 3:
                await message.channel.send("ゲームが終了しました！\nまた遊びたいときは「hearts!start」と送信してください。")
                return


def is_int(s):  # 整数値を表しているかどうかを判定
    try:
        int(s, 10)  # 文字列を実際にint関数で変換してみる
    except ValueError:
        return False  # 例外が発生＝変換できないのでFalseを返す
    else:
        return True  # 変換できたのでTrueを返す


client.run(os.environ['TOKEN'])