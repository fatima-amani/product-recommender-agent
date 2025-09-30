from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage

from bson import ObjectId, Decimal128, Binary
import datetime, base64


def run_llm(llm_model, pydantic_model, system_msg="", human_msg="", parameters={}):
    parser = PydanticOutputParser(pydantic_object=pydantic_model)
    format_instructions = parser.get_format_instructions()

    system_msg += f"Format Instruction: \n {format_instructions}"

    system_msg = SystemMessage(content=system_msg)
    human_msg = HumanMessage(content=human_msg)


    prompt = ChatPromptTemplate.from_messages([system_msg, human_msg])

    llm=ChatGoogleGenerativeAI(model=llm_model)
    
    chain = prompt | llm | parser

    result = chain.invoke({
        **parameters,
        "format_instructions": format_instructions,
    })

    
    return result

def serialize(value):
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    if isinstance(value, Decimal128):
        return float(value.to_decimal())
    if isinstance(value, Binary):
        return base64.b64encode(bytes(value)).decode("ascii")
    if isinstance(value, dict):
        return {k: serialize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serialize(v) for v in value]
    return value


