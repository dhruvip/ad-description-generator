from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
from langchain.chains import LLMChain
import os
from langchain_community.callbacks import get_openai_callback

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
    template_string = '''
    Imagine you are support team member for a classifieds platform where sellers can post ads for different products they 
    want to sell or rent out.
    You are responsible for helping sellers in curate proper product description for a classifieds site, where you effectively communicate the value and specifics of the product to potential buyers in English, Sinhala, Tamil or Bangala language. Please follow best practices as mentioned below. 
    The product description should be generated keeping in mind the ad specifics as mentioned in the request.
    Please note that the price specified in ad specifics is in local currency (Lankan Rupees LKR or Bangladeshi Taka TK)

    BEST PRACTICES:
    - Keep your description straightforward and to the point. Avoid unnecessary jargon and technical terms.
    - Create a catchy and descriptive title that includes the product's name, key features, or brand. Ensure the title accurately reflects what the buyer can expect.
    - List essential specifications, dimensions, and attributes. Highlight the unique selling points and benefits of the product.
    - Explain how the product solves a problem or enhances the buyer's life. Provide scenarios or uses that illustrate its benefit.
    - Clearly state the condition of the product (new, used, refurbished). Mention any defects or issues honestly to build trust with potential buyers.
    - Break up text with bullet points for easy scanning of key features or benefits. Use short paragraphs to make the description less intimidating.
    - Use relevant keywords naturally within the text to improve searchability. Avoid keyword stuffing, which can make the description hard to read.
    - Encourage potential buyers to take the next step by contacting you or making an offer.
    - Check for spelling and grammatical errors to maintain professionalism.

    Avoid making up answers. If factual data is not available, output "I dont know".

    Can you help me write product description for {ad_type} {category} with brand and model {brand_model} in language {language} with ad specifics in the format key: value as below
    AD SPECIFICS:
    {ad_specifics}
    If the values in ad specifics are not provided please use factual data 

    Also, give a comma separated list of search keywords for the generated ad description
    '''
    session_obj, ad_specifics = copy_and_clean_session_obj(session_obj, ["ad_type","category","brand-model","language","generate"])

    
    # chat = ChatOpenAI(temperature=0.0, model='gpt-3.5-turbo')
    prompt_template = ChatPromptTemplate.from_template(template_string)
    print(prompt_template.messages[0].prompt.input_variables)
    final_prompt = prompt_template.format_messages(
                    ad_type=session_obj["ad_type"],
                    brand_model=session_obj["brand-model"],
                    category=session_obj["category"],
                    ad_specifics=ad_specifics,
                    language=session_obj["language"]
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
                max_new_tokens=128, 
                temperature=0.5,
                huggingfacehub_api_token=hf_token,
            )

            response = llm.invoke(final_prompt[0].content)
            call_details = f"Total Tokens: {cb.total_tokens} Prompt Tokens: {cb.prompt_tokens} Completion Tokens: {cb.completion_tokens} Total Cost (USD): ${cb.total_cost}"
    except:
        response = 'Some Error occured while calling Hugging face'
        call_details = 'None'
    return response, final_prompt, call_details