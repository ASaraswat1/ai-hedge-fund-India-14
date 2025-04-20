
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

def peter_lynch_agent(df):
    try:
        prompt = ChatPromptTemplate.from_template(
            "You are a trading strategy agent. Analyze the following stock data and return binary trading signals (0 or 1):\n{data}"
        )
        llm = ChatOpenAI(temperature=0)
        input_text = prompt.format(data=df.tail(5).to_string())
        response = llm.invoke(input_text)

        # Fallback: if LLM returns string or bad format
        if not hasattr(response, "content"):
            return df["Close"].apply(lambda x: 1)
        content = response.content

        # Placeholder: actual signal extraction would go here
        return df["Close"].apply(lambda x: 1 if x > df["Close"].mean() else 0)

    except Exception as e:
        print("Error in peter_lynch_agent:", e)
        return df["Close"].apply(lambda x: 1)
