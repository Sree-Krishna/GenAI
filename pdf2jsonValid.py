import os, tiktoken, json
from processdata import extract_text_from_pdfplumber, extract_text_from_pymupdf
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser, RetryOutputParser
from pydanticschema import ResumeData  # Importing the Pydantic schema

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
model_name = "gpt-4o-mini-2024-07-18"
# model_name = "gpt-3.5-turbo"

# Initialize the LLM
model = ChatOpenAI(
    model_name=model_name, 
    openai_api_key=openai_api_key,
    temperature=0  # Set to 0 for deterministic output,
)

# Define the PydanticToolsParser for the ResumeData schema
parser = JsonOutputParser(pydantic_object=ResumeData)

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
    input_variables=['resume_text'],
    template=template,
    partial_variables={"json_schema": parser.get_format_instructions()},
)

# LLM chain using the defined prompt and parser
def parse_resume(resume_text):
    try:
        # Create the chain with the prompt and LLM
        chain = resume_prompt | model | parser

        # Run the chain to get the output
        output = chain.invoke({"resume_text": resume_text})
        print('extracted resume', output)
        return output

    except Exception as e:
        print(f"LLM failed to generate output: {e}")
        print(f"Error parsing and validating output: {e}")
        # Output fixing parser to handle invalid output and correct it with the LLM
        prompt_value = resume_prompt.format_prompt(resume_text=resume_text)
        retry_parser = RetryOutputParser.from_llm(parser=parser, llm=model)
        resume_json = retry_parser.parse_with_prompt(output, prompt_value)
        print("Validated and Corrected Output:")
        print('extracted resume after correction', resume_json)
        return resume_json



# pdf_path = 'Sree_Krishna_Resume_Infosys.pdf' 
# pdf_path = 'yama.pdf' 
# pdf_path = 'resume_juanjosecarin.pdf' 
# pdf_path = 'ilia.pdf'
# pdf_path = 'resume.pdf'
pdf_path = 'das.pdf'
# resume_text = extract_text_from_pypdf(pdf_path)
# resume_text = extract_text_from_pdfplumber('data/'+pdf_path)
resume_text = extract_text_from_pymupdf('data/'+pdf_path)


resume_data = parse_resume(resume_text)
if resume_data:
    print("Parsed Resume Data:")
    print(json.dumps(resume_data, indent=4))
    with open("outputs/"+pdf_path[:-4]+".json", "w") as f:
        json.dump(resume_data, f, indent=4)
else:
    print("Could not parse resume data.")
