import os
import google.generativeai as genai

def summarize_text(text):
    # Load the API key from the environment variable
    api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GOOGLE_GEMINI_API_KEY is not set in the environment variables.")

    # Configure the Generative AI library with the API key
    genai.configure(api_key=api_key)

    try:
        # Instantiate the model
        model = genai.GenerativeModel("gemini-1.5-flash")  # Use the correct model as per your documentation
        # Generate a summary for the text
        response = model.generate_content(f"Analyze the following text:\n\n{text}")

        # Extract and return the summarized text
        return response.text
    except Exception as e:
        print(f"Error during text summarization: {e}")
        raise


def routine_generator(query):
    """
    Generates a routine using Google Gemini API.
    
    :param query: The query for routine generation.
    :return: The generated routine.
    """
    # Load the API key from the environment variable
    api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GOOGLE_GEMINI_API_KEY is not set in the environment variables.")

    # Configure the Generative AI library with the API key
    genai.configure(api_key=api_key)

    try:
        # Instantiate the model
        model = genai.GenerativeModel("gemini-1.5-flash")  # Adjust model name as per documentation
        # Generate routine content
        response = model.generate_content(query)

        # Return the generated content
        return response.text
    except Exception as e:
        print(f"Error during routine generation: {e}")
        raise
