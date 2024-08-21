import os
from llama_index.llms.gemini import Gemini
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.llms.vertex import Vertex
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import (
    StructuredPlannerAgent,
    FunctionCallingAgentWorker,
    ReActAgent,
    AgentRunner
)

from google.oauth2 import service_account

from tools.retrieval.get_db_schema import get_db_schema
from tools.retrieval.get_programs import get_programs
from tools.retrieval.get_potential_schedules import get_potential_schedule
from tools.retrieval.get_rmp_professor_info import get_rmp_professor_info
from tools.retrieval.get_courses import get_courses
from tools.retrieval.get_courses_for_program import get_courses_for_program
from tools.retrieval.get_schedule_link import get_schedule_link
from tools.retrieval.get_course_overview_for_schedule import get_course_overview_for_schedule

from tools.retrieval.helpers.db import get_db

from dotenv import load_dotenv
load_dotenv()

AZURE_OPENAI_API_KEY =                  os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_API_URI =                  os.getenv('AZURE_OPENAI_API_URI')
AZURE_OPENAI_API_DEPLOYMENT_NAME =      os.getenv('AZURE_OPENAI_API_DEPLOYMENT_NAME')
AZURE_OPENAI_API_VERSION =              os.getenv('AZURE_OPENAI_API_VERSION')
AZURE_OPENAI_MODEL =                    os.getenv('AZURE_OPENAI_API_MODEL')

GEMINI_API_KEY =                        os.getenv('GEMINI_API_KEY')
GEMINI_MODEL =                          os.getenv('GEMINI_MODEL')

def get_tools():
    tools = [FunctionTool.from_defaults(tool) for tool in [
        get_db_schema,
        get_programs,
        get_potential_schedule,  ## CURRENTLY NOT WORKING
        get_rmp_professor_info,
        get_courses,
        get_courses_for_program,
        get_schedule_link,
        get_course_overview_for_schedule
    ]]
    return tools

def get_llm():
    filename = 'google-credentials.json'
    credentials = service_account.Credentials.from_service_account_file(filename)
    llm = Vertex(
        credentials=credentials,
        model='gemini-1.5-flash',
        project=credentials.project_id,
    )
    # if not AZURE_OPENAI_API_KEY:
    #     llm = Gemini(
    #         api_key=GEMINI_API_KEY,
    #         model=GEMINI_MODEL,
    #     )
    # else:
    #     llm = AzureOpenAI(
    #         api_key=AZURE_OPENAI_API_KEY,
    #         azure_endpoint=AZURE_OPENAI_API_URI,
    #         deployment_name=AZURE_OPENAI_API_DEPLOYMENT_NAME,
    #         api_version=AZURE_OPENAI_API_VERSION,
    #         model=AZURE_OPENAI_MODEL
    #     )
    return llm

def get_planner_agent():
    worker = FunctionCallingAgentWorker.from_tools(
        tools=get_tools(),
        llm=get_llm(),
        verbose=True
    )
    planner_agent = StructuredPlannerAgent(
        agent_worker=worker,
        tools=get_tools(),
        llm=get_llm(),
        verbose=True
    )
    return planner_agent

def get_agent_runner():
    worker = FunctionCallingAgentWorker.from_tools(
        tools=get_tools(),
        llm=get_llm(),
        verbose=True
    )
    return AgentRunner(agent_worker=worker, llm=get_llm(), verbose=True)

def get_react_agent():
    react_agent = ReActAgent.from_tools(
        tools=get_tools(),
        llm=get_llm(),
        verbose=True,
        max_iterations=15
    )
    return react_agent

if __name__ == '__main__':
    
    # print(get_agent_runner().chat("Can you tell me which courses are in the SOFTENG-BS program?"))
    print(get_react_agent().chat("Can you give me information on a schedule with the courses CSCI-141, CSCI-142 and GCIS-123? Please give me professor ratings for each course as well. Try to make it a report style response, with as much information as possible."))
