from crewai import Crew, Agent, Task, Process
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="deepseek-chat", 
    verbose=True, 
    temperature = 0,
    streaming=True,
    max_tokens=4096
    )

agent = Agent(
  role='Data Analyst',
  goal='Extract actionable insights',
  backstory="""You're a data analyst at a large company.
  You're responsible for analyzing data and providing insights
  to the business.
  You're currently working on a project to analyze the
  performance of our marketing campaigns.""",
  llm=llm
  
    )
task = Task(
    description='Find and summarize the latest and most relevant news on AI',
    agent=agent,
    expected_output='A bullet list summary of the top 5 most important AI news',
)
my_crew = Crew(
    agents=[agent],
    tasks=[task],
    process=Process.sequential,
    memory=True,
    verbose=True,
    llm=llm,
    manager_llm=llm
)

my_crew.kickoff()