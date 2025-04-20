
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

def portfolio_management_agent(df):
    try:
        prompt = ChatPromptTemplate.from_template("Given historical prices in the form of a pandas dataframe, provide a binary trading signal (0 or 1) for each row. Data:{data}")
        llm = ChatOpenAI(temperature=0)
        input_text = prompt.format(data=df.tail(5).to_string())

        response = llm.invoke(input_text)

        print("LLM raw response:", response)

        # If response is not structured, fallback
        if not response or not hasattr(response, "content"):
            print("Fallback triggered: empty response or no .content")
            return df["Close"].apply(lambda x: 1)

        # TODO: Parse response.content if it contains a signal array
        return df["Close"].apply(lambda x: 1 if x > df["Close"].mean() else 0)

    except Exception as e:
        print("LLM ERROR:", e)
        return df["Close"].apply(lambda x: 1)
