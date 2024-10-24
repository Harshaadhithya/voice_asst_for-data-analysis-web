from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
import pandas as pd
import os



def main():
    OPENAI_API_KEY = ''
    df1 = pd.read_csv('Dataset/PATIENTS.csv')
    llm = ChatOpenAI(model='gpt-3.5-turbo-1106', api_key=OPENAI_API_KEY, temperature=0)
    agent = create_pandas_dataframe_agent(llm=llm, df=df1, verbose=True, allow_dangerous_code=True)
    print(agent.invoke("How many male and female patients are there?"))

if __name__ == '__main__':
    main()