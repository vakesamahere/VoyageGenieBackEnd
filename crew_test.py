from crewai import Crew, Agent, Task, Process
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory

print('LLM loading')
llm = ChatOpenAI(
    model="deepseek-chat", 
    verbose=True, 
    temperature = 0,
    streaming=True,
    max_tokens=4096
    )
print(f'LLM loaded: {llm}')

print("loading agent")
memory = ConversationBufferMemory()

agent = Agent(
    role="person",
    goal="""calculate""",
    backstory="I am a man",
    llm=llm,
    memory=memory  # 在 Agent 级别设置记忆
)
# agent = Agent(
#         role="person",
#         goal="talk something",
#         backstory="I am a man",
#         llm=llm
#     )
print(f"agent loaded: {agent}")


print("loading task")
task = Task(
    description="""calculate the square of {history}""",
    agent=agent,
    expected_output='a number',
    llm=llm
)
print(f"task loaded: {task}")

print('loading crew')
crew = Crew(
    agents=[agent],
    tasks=[task],
    process=Process.sequential,
    verbose=True,
    # 不要在这里设置 memory 参数
)
# crew = Crew(
#     agents=[agent],
#     tasks=[task],
#     process=Process.sequential,
#     verbose=True,
#     #===========================================加了下一行报错==========================
#     # memory=True, 
# )
print(f"crew loaded: {crew}")

crew.kickoff(inputs={
    "history":"3"
})
crew.kickoff()