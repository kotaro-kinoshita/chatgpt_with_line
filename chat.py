import json
from distutils.util import strtobool

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain import PromptTemplate, LLMChain

from langchain.memory import (
    ConversationBufferWindowMemory
)

from langchain.prompts.chat import (
    ChatPromptTemplate,
    MessagesPlaceholder, 
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from langchain.agents import (
    load_tools,
    ZeroShotAgent,
    AgentExecutor
)

from langchain import PromptTemplate, FewShotPromptTemplate

from langchain.schema import messages_from_dict, messages_to_dict

class ChatGPT:
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0.):
        self.chat_model = ChatOpenAI(
            model_name=model_name, 
            temperature=temperature
        )

        self.memory = ConversationBufferWindowMemory(
            k=3, 
            return_messages=True,
        )

        self.tools = load_tools(
            ["serpapi"], 
            llm=self.chat_model
        )

    def system_message_prompt(self):
        system_template =  "必要に応じて、一つ前のシステムメッセージの検索結果の情報を参照して、情報をなんｊ民風に変換して回答してください。検索情報が「No infomation」の場合は、情報を参照せずにメッセージになんj民風に返答してください"
        return SystemMessagePromptTemplate.from_template(system_template)

    def answer_message_prompt(self, answer):
        answer_template = answer
        return SystemMessagePromptTemplate.from_template(answer_template)

    def human_message_prompt(self):
        human_template = "{input}"
        return HumanMessagePromptTemplate.from_template(human_template)

    def is_quesion(self, message):
        system_template = "メッセージの内容が質問であるかないか判定してください。メッセージが質問であればTrue、メッセージが質問ではなければFalseを応答してください。"

        example_formatter_template = """
        message: {message}
        answer: {answer}\n
        """

        example_prompt = PromptTemplate(
            input_variables=["message", "answer"],
            template=example_formatter_template,
        )

        examples = [
            {"message": "今日の天気は？", "answer": "True"},
            {"message": "おはよう", "answer": "False"},
            {"message": "明日の日付を教えて", "answer": "True"},
            {"message": "今日はいい天気だね", "answer": "False"},
        ]

        few_shot_prompt = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            prefix=system_template,
            suffix="message: {input}\nanswer:",
            input_variables=["input"],
            example_separator="\n\n",
        )

        chain = LLMChain(
            llm=self.chat_model, 
            prompt=few_shot_prompt
        )

        result = chain.run(input=message)

        return strtobool(result)


    def execute_agent(self, message):
        agent_prompt = ZeroShotAgent.create_prompt(
            self.tools,
            prefix="""質問の内容をツールを使用して日本語で検索してください。情報が見つからないときは「no infomation」を返してください。 
            タイムゾーンはTokyoを使用してください。
            """,
            suffix="""始めましょう！
            Question: {input}
            検索結果「{agent_scratchpad}」
            """,
            input_variables=["input", "agent_scratchpad"]
        )

        agent_chain = LLMChain(
            llm=self.chat_model,
            prompt=agent_prompt
        )

        agent = ZeroShotAgent(
            llm_chain=agent_chain, 
            tools=self.tools, 
            verbose=True
        )

        agent_chain = AgentExecutor.from_agent_and_tools(
            agent=agent, 
            tools=self.tools, 
            max_iterations=2,
            verbose=True, 
        )

        try:
           answer = agent_chain.run(input=message)
        except ValueError as e:
           answer = "No infomation"
            
        return answer

    def __call__(self, message, logger):
        logger.info(message)
        
        if self.is_quesion(message):
            answer = self.execute_agent(message)
        else:
            answer = "No infomation"

        logger.info(answer)

        answer_prompt = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name="history"),
            self.answer_message_prompt(answer),
            self.system_message_prompt(),
            self.human_message_prompt(),
        ])

        answer_chain = ConversationChain(
            llm=self.chat_model,
            prompt=answer_prompt,
            memory=self.memory
        )

        result=answer_chain.predict(input=message)

        logger.info(self.memory.load_memory_variables({}))
        logger.info(answer)

        return result

#import logging#
#logger = logging.getLogger()
#logger.setLevel(logging.INFO)#
#chat = ChatGPT()
#print(chat("大谷さんすごいね", logger))
#print(chat("今日はどうだったの？", logger))
