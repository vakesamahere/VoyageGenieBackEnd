from crewai import Crew, Agent, Task, Process
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
load_dotenv()

print('LLM loading')
llm = ChatAnthropic(
    model="claude-3-5-sonnet@20240620", 
    verbose=True, 
    temperature = 0,
    top_p=0.9,
    max_tokens=4096,
    streaming=True
)
print(f'LLM loaded: {llm}')

print("loading agent")
memory = ConversationBufferMemory()

agent = Agent(
    role="person",
    goal="""calculate""",
    backstory="I am a man",
    llm=llm
)
print(f"agent loaded: {agent}")


print("loading task")
task = Task(
    description="""cal the sqaure of {number} and the number in your memory""",
    agent=agent,
    expected_output='numbers',
    llm=llm
)
print(f"task loaded: {task}")

print('loading crew')
crew = Crew(
    agents=[agent],
    tasks=[task],
    process=Process.sequential,
    verbose=True,    
    memory=True,
    embedder={
        "provider": "openai",
        "config":{
            "model": 'text-multilingual-embedding-002'
        }
    }
)
print(f"crew loaded: {crew}")

crew.kickoff(inputs={
    "number":"3"    # expect:9,0
})
crew.kickoff(inputs={
    "number":"none" # expect:0,9
})