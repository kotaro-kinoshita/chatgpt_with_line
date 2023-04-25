# ChatGPT with LINE

## 内容

ChatGPTのAPIをLINEで呼び出し、LINE経由で会話するデモの試作

- 答えられない情報は、LangChainのAgent機能: [ReAct](https://arxiv.org/abs/2210.03629) を使ってSerpAPIを呼び出し、最新の情報を参照する
- メモリーを参照し、過去の会話ログ情報を参照し、会話する
- 特定の口調で返答する

## 構成

- LINE Messaging APIからAWS lambdaにチャットの情報を転送
- LambdaからLangChain経由でGPT3.5のAPIにアクセスし、返答
- 答えられない最新の情報はSeapAPIで検索を実施して返答

<img src="https://github.com/kotaro-kinoshita/chatgpt_with_line/blob/main/img/system.png">

## デモ

GPT3.5のデータに含まれていない最近の情報をSerpAPI経由で取得し、返答できることを確認
<img src="https://github.com/kotaro-kinoshita/chatgpt_with_line/blob/main/img/demo.PNG">
