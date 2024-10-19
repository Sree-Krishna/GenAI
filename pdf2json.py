import os, tiktoken, json
from processdata import extract_text_from_pdfplumber
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
model_name = "gpt-4o-mini-2024-07-18"
# model_name = "gpt-3.5-turbo"

# Initialize the LLM
llm = ChatOpenAI(
    model_name=model_name, 
    openai_api_key=openai_api_key,
    temperature=0  # Set to 0 for deterministic output,
)

# new feature structuredata is available using pydantic as of recent
llm = llm.bind(response_format={"type": "json_object"})

json_schema = ''
# Load the schema from a file
with open("schema.json", "r") as file:
    json_schema = json.load(file)
json_schema = json.dumps(json_schema)


template = """
    You are an expert at converting resume text into structured data. Use the provided JSON schema to ensure the output follows the correct format.

    Here is the parsed resume text:

    \"\"\"
    {resume_text}
    \"\"\"

    Use the following schema to generate the structured JSON:

    \"\"\"
    {json_schema}
    \"\"\"

    Guidelines:
    - If any information is missing or incomplete, leave those fields as null.
    - Only extract what is present in the resume text. Do not generate or infer information that is not explicitly stated.
    - Ensure names are in lowercase.
    - Extract the email as it appears, ensuring it is case-sensitive.
    - Phone numbers should be formatted as +1 (xxx) xxx-xxxx.
    - For websites, create a dictionary with keys: 'github', 'linkedin', 'portfolio', 'others', and use null if not available.
    - For the professional summary, if it is not found, set it as null.
    - Dates should follow the format: month/year.
    - Work experience should list all responsibilities mentioned and include location as city, state, and country.
    - For skills, extract individual skills and split them up dont ever group them, remove paranthesis or brackes if any.
    - for example strictly remove headings or section sub headings within skills like programming, machine learing etc.
    - Ensure that the JSON is properly formatted, valid, and follows the schema precisely.


    Ensure the output is in valid JSON format based on the schema and schema is for reference only and do not include keys like properties, type, description .

    JSON Output:
    """

resume_prompt = PromptTemplate(
    input_variables=['resume_text', 'json_schema'],
    template=template
)

def parse_resume(resume_text):
    try:
        # Create an instance of LLMChain with the prompt and LLM
        chain = resume_prompt | llm
        
        # Run the chain to get the LLM's output
        output = chain.invoke({"resume_text":resume_text, "json_schema":json_schema})
        
        # Attempt to parse the output as JSON
        try:
            resume_json = json.loads(output.content)
        except json.JSONDecodeError:
            print("Failed to parse JSON. LLM output was:")
            print(output)
            resume_json = None
        return resume_json
    except:
        print('llm failed to generate output')
        return ''



# pdf_path = 'Sree_Krishna_Resume_Infosys.pdf' 
# pdf_path = 'yama.pdf' 
pdf_path = 'resume_juanjosecarin.pdf' 
# resume_text = extract_text_from_pypdf(pdf_path)
resume_text = extract_text_from_pdfplumber('data/'+pdf_path)

resume_data = parse_resume(resume_text)

if resume_data:
    print("Parsed Resume Data:")
    print(json.dumps(resume_data, indent=4))
    with open("outputs/"+pdf_path[:-4]+".json", "w") as f:
        json.dump(resume_data, f, indent=4)
else:
    print("Could not parse resume data.")





###############
# Chencking how many tokents are sent to the model
# Convert the JSON object back to string format 
tokens_str = template+ json.dumps(json_schema) + str(resume_data)

# Use tiktoken's encoding for the model
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
token_count = len(encoding.encode(tokens_str))
print(f"Number of tokens: {token_count}")
###############