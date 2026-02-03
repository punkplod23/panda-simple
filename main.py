import pandas as pd
import re

def answer_csv_question_rule_based(csv_file, question):
    df = pd.read_csv(csv_file)
    question = question.lower()

    if "how many products" in question or "count products" in question:
        return f"There are {len(df)} products."
    elif "price of" in question:
        # Extract product name
        match = re.search(r"price of (.+?)\?", question)
        if match:
            product_name = match.group(1).strip()
            # Simple direct match - consider fuzzy matching for real apps
            result = df[df['company_name'].str.lower() == product_name.lower()]['price']
            if not result.empty:
                return f"The price of {product_name} is {result.iloc[0]}."
            else:
                return f"Sorry, I couldn't find the price for {product_name}."
        else:
            return "Please specify which product you're asking about."
    elif "what are the products" in question:
        return "The products are: " + ", ".join(df['product_name'].tolist())
    # Add more rules as needed for other columns/operations
    else:
        return "Sorry, I can only answer simple questions about product price or count."



print(answer_csv_question_rule_based('test.csv', "What is the price of Laptop?"))
# print(answer_csv_question_rule_based('products.csv', "How many products do you have?"))
# print(answer_csv_question_rule_based('products.csv', "What are the products?"))
# print(answer_csv_question_rule_based('products.csv', "Tell me about the stock.")) # Will return generic message