from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
from langchain.chains import LLMChain
import os
from langchain_community.callbacks import get_openai_callback
from prompts import general_prompt_template, vehicle_prompt_template, auto_parts_prompt_template
import logging

def copy_and_clean_session_obj(session_obj, nonspecifics):
    temp = dict()
    for _e in session_obj:
        temp[_e] = session_obj[_e]
    all_keys = set(temp.keys())
    specifics = all_keys.difference(nonspecifics)
    temp["brand-model"] = temp["brand-model"].replace("-"," ")
    specifics_str = ""
    for _e in specifics:
        if temp[_e] not in ["",[]]:
            specifics_str = specifics_str + f'- {_e}: {temp[_e]}\n'
    return temp, specifics_str

def generator(session_obj, model):
    print("==============================")
    print(session_obj)
    print("==============================")
    session_obj, ad_specifics = copy_and_clean_session_obj(session_obj, ["ad_type","category","brand-model","language","location","generate"])
    
    if(session_obj["category"] in ["Cars", "Motorbikes"]):
        template_string = vehicle_prompt_template.prompt
    else:
        template_string = general_prompt_template.prompt
    
    prompt_template = ChatPromptTemplate.from_template(template_string)
    print(prompt_template.messages[0].prompt.input_variables)
    final_prompt = prompt_template.format_messages(
                    ad_type=session_obj["ad_type"],
                    brand_model=session_obj["brand-model"],
                    category=session_obj["category"],
                    ad_specifics=ad_specifics,
                    language=session_obj["language"],
                    location=session_obj["location"]
                    )
    match model:
        case 'gpt-4o':
            return chatGpt(final_prompt, model='gpt-4o')
        case 'gpt-4o-mini':
            return chatGpt(final_prompt, model='gpt-4o')
        case 'gpt-3.5-turbo':
            return chatGpt(final_prompt, model='gpt-3.5-turbo')
        case 'mistralai':
            return huggingFace(final_prompt, model='mistralai/Mistral-7B-Instruct-v0.2')
        case _:
            print('default case')

def chatGpt(final_prompt,model):
    try:
        chat = ChatOpenAI(temperature=0.0, model=model)
        with get_openai_callback() as cb:
            description = chat.invoke(final_prompt)
            call_details = f"Total Tokens: {cb.total_tokens} Prompt Tokens: {cb.prompt_tokens} Completion Tokens: {cb.completion_tokens} Total Cost (USD): ${cb.total_cost}"

    except:
        description={}
        description['content'] = 'Some Error occured while calling Chat gpt'
        call_details = 'None'
    return description.content, final_prompt,call_details

def huggingFace(final_prompt, model):
    repo_id = model
    hf_token = os.getenv('HF_TOKEN')
    try:
        with get_openai_callback() as cb:
            llm = HuggingFaceEndpoint(
                repo_id=repo_id,
                max_new_tokens=250, 
                temperature=0.5,
                huggingfacehub_api_token=hf_token,
            )

            response = llm.invoke(final_prompt[0].content)
            call_details = f"Total Tokens: {cb.total_tokens} Prompt Tokens: {cb.prompt_tokens} Completion Tokens: {cb.completion_tokens} Total Cost (USD): ${cb.total_cost}"
    except:
        response = 'Some Error occured while calling Hugging face'
        call_details = 'None'
    return response, final_prompt, call_details