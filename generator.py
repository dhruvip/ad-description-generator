from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
from langchain.chains import LLMChain

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

def generator(session_obj):
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
    '''
    session_obj, ad_specifics = copy_and_clean_session_obj(session_obj, ["ad_type","category","brand-model","language"])

    
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
    
    chatGpt(final_prompt)
    huggingFace(final_prompt)

def chatGpt(final_prompt):
    chat = ChatOpenAI(temperature=0.0, model='gpt-4o')
    description = chat.invoke(final_prompt)
    return description.content, final_prompt

def huggingFace(final_prompt):
    repo_id = "mistralai/Mistral-7B-Instruct-v0.2"

    llm = HuggingFaceEndpoint(
        repo_id=repo_id,
        max_length=128,
        temperature=0.5,
        huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN,
    )

    response = llm.invoke(final_prompt[0].content)
    return response, final_prompt