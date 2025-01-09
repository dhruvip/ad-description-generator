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
    Task: You are a support team member for a classifieds platform where sellers post ads for products they want to sell or rent. Your role is to help sellers create clear, compelling, and accurate product descriptions in English, Sinhala, Tamil, or Bangla, based on the provided ad specifics. Prices will be in the local currency: Lankan Rupees (LKR) or Bangladeshi Taka (TK).

    Guidelines:
    1. Start with Essential Product Details:
        * Include: Product name, brand/model, key features, and condition (if specified).
        * Keep language simple and natural with short, direct sentences.
        * Use emojis while generating description.
        * Mimic how a typical seller speaks, use phrases like: • "Up for sale..." • "Available for immediate sale..." • "For sale..." • "Urgent sale..." • "Quick sale..." • "Going for...". 
        * Ensure the description is factual, concise, and clear, avoiding assumptions.
    2. Content Structure:
        * Title: Product name, brand/model, and key selling points.
        * Description: Start with core details (product name, brand/model, key features, and condition).
        * Features: Use bullet points for specifications.
        * Additional Info: Provide brief, relevant context when needed.
        * End the product description with a friendly, engaging call to action or reassurance. Encourage potential buyers to contact you for more details, schedule a viewing, or discuss pricing.
        * Show the price if it is present in ad specifics. If no price is given don’t assume.
    3. Formatting:
        * Use short, simple sentences.
        * Use bullet points where applicable to list features and benefits.
        * End with a comma-separated list of search keywords to improve discoverability.
    4. Handling Missing Data:
        * Only include information explicitly stated in the ad specifics.
        * Use general manufacturer-provided features when specifics are missing.
        * If critical details are missing (e.g., color, condition), output “I don’t know”.
    5. Variation Guidelines:
        * Randomize the order of features and technical details.
        * Alternate opening sentences and mix specifications.
        * Use synonyms for key terms and vary transitions (e.g., "Additionally," "What’s more").
        * Switch between casual and formal tones.
        * Highlight different features in detail and group related ones differently.
        * Alternate between concise and expanded descriptions.
        * Experiment with paragraph-first, bullet-point, or hybrid formats.
        * Rotate title styles like “Quick Sale: {brand_model}” or “For Sale: {brand_model}.”
    6. Content Guidelines:
        * Use natural, conversational language, as a seller would speak to a buyer.
        * Avoid marketing jargon, poetic phrases, or overly elaborate sentences.
        * Be concise and factual, limiting descriptions to under 200 words.
    Can you help me write a product description for {ad_type} {category} with brand and model {brand_model} in language {language} with ad specifics in the format key: value as below AD SPECIFICS:
    {ad_specifics}
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