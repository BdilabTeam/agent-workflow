from typing import Optional, Callable, Union
from langflow import CustomComponent
from langflow.field_typing import Tool
from langchain.agents import AgentExecutor, StructuredChatAgent
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langchain.llms.base import BaseLanguageModel
from langchain_core.memory import BaseMemory



class SingleAgent(CustomComponent):
    display_name = "智能体Agent节点"
    def build_config(self):
        return {
        }

    def build(
        self, 
        llm: BaseLanguageModel,
        memory: BaseMemory,
        system_prompt: Optional[str] = "",
        tool: Optional[Tool] = [],
        knowledge: Optional[Tool] = [],
        workflow: Optional[Tool] = [],
    ) -> Union[AgentExecutor, Callable]:
        
        tools = tool + knowledge + workflow

        # prompt = ChatPromptTemplate.from_messages(
        #     [
        #         SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=[], template=system_prompt)), 
        #         MessagesPlaceholder(variable_name='history', optional=True), 
        #         # MessagesPlaceholder(variable_name='input'), 
        #         HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template='{input}')), 
        #         MessagesPlaceholder(variable_name='agent_scratchpad')
        #     ]
        # )
        if system_prompt == "":
            prefix = """你是一位智能助手，请通过你自己的知识和调用工具解决问题,回答调用一个工具或者不调用任何工具,全部回答请用中文：""" 
        else:
            prefix = system_prompt
        suffix = """
                {chat_history}
                {input}
                {agent_scratchpad}"""
                
        prompt = StructuredChatAgent.create_prompt(
            tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=["input", "chat_history", "agent_scratchpad"],
        )
        llm_chain = LLMChain(llm=llm, prompt=prompt)
 
        agent = StructuredChatAgent(llm_chain=llm_chain, tools=tools)
        return AgentExecutor.from_agent_and_tools(agent=agent, memory=memory, tools=tools, handle_parsing_errors=True, verbose=True)
        
        # agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)
        # return AgentExecutor.from_agent_and_tools(agent=agent, memory=memory, tools=tools, handle_parsing_errors=True, verbose=True)
        
        
        
        # return initialize_agent(
        #     tools=tools,
        #     memory=memory,
        #     llm=llm,
        #     agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        #     return_intermediate_steps=False,
        #     handle_parsing_errors=True,
        #     max_iterations=5,
        #     verbose=True
        # )